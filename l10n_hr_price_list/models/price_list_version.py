import hashlib
import hmac
import json
import logging
from datetime import timedelta
from urllib.parse import quote

import pytz
import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

TZ = pytz.timezone("Europe/Zagreb")
# Previous price lists must stay public at least 30 days after their publication.
KEEP_DAYS = 30
WEBHOOK_TIMEOUT = 15

# Prescribed content (Ministry of Economy explanation of NN 101/26, point 2.5): the same
# structure for every premises, product and service columns together.
COLUMNS = [
    "sifra",
    "naziv",
    "marka",
    "jedinica_mjere",
    "maloprodajna_cijena_eur",
    "cijena_za_jedinicu_mjere_eur",
    "jedinica_mjere_za_cijenu",
    "posebni_oblik_prodaje",
    "naziv_posebnog_oblika_prodaje",
    "dodatna_cijena_eur",
    "datum_dodatne_cijene",
    "barkod",
    "raspolozivost",
]
# Sent on the webhook only (not in the prescribed file): sales price without taxes, e.g. for showing
# prices to companies on the website.
NET_COLUMN = "prodajna_cijena_bez_pdv_eur"
# Sent on the webhook only, during a special sale: price before the sale and the lowest price in the 30 days
# before it (to be shown next to the special sale price).
PRICE_BEFORE_SALE_COLUMN = "cijena_prije_posebnog_oblika_prodaje_eur"
LOWEST_PRICE_COLUMN = "najniza_cijena_30_dana_eur"
# Saved with the rows (to find a product in earlier versions), not published.
PRODUCT_KEY = "_product_id"


def format_amount(value):
    return f"{value:.2f}".replace(".", ",")


def parse_amount(value):
    return float(value.replace(",", ".")) if value else 0.0


def public_rows(rows):
    """Rows without the keys that are saved but not published."""
    return [{key: value for key, value in row.items() if key != PRODUCT_KEY} for row in rows]


def format_date(value):
    return value.strftime("%d.%m.%Y") if value else ""


def local_time(value):
    """A UTC datetime (as stored by Odoo) in Zagreb time."""
    return pytz.utc.localize(value).astimezone(TZ)


def local_now():
    return local_time(fields.Datetime.now())


class L10nHrPriceListVersion(models.Model):
    _name = "l10n_hr.price.list.version"
    _description = "Public Price List Version"
    _order = "location_id, number desc"

    location_id = fields.Many2one(
        "l10n_hr.price.list.location", string="Premises", required=True, readonly=True, index=True,
        ondelete="restrict",
    )
    company_id = fields.Many2one(related="location_id.company_id", store=True, index=True)
    number = fields.Integer(string="Storage Number", required=True, readonly=True)
    name = fields.Char(string="File Name", required=True, readonly=True, index=True)
    published_at = fields.Datetime(string="Published", required=True, readonly=True)
    file = fields.Binary(string="File", attachment=True, readonly=True)
    checksum = fields.Char(readonly=True)
    rows_json = fields.Text(string="Rows (JSON)", readonly=True)
    line_count = fields.Integer(string="Lines", readonly=True)
    is_current = fields.Boolean(string="Current", compute="_compute_is_current")
    url = fields.Char(string="Public Link", compute="_compute_url")
    webhook_state = fields.Selection(
        selection=[
            ("none", "Not used"),
            ("pending", "Waiting"),
            ("sent", "Sent"),
            ("error", "Error"),
        ],
        string="Webhook",
        default="none",
        required=True,
        readonly=True,
    )
    webhook_error = fields.Char(string="Webhook Error", readonly=True)
    webhook_sent_at = fields.Datetime(string="Sent to Webhook", readonly=True)

    _location_number_uniq = models.Constraint(
        "UNIQUE(location_id, number)",
        "The storage number of a price list must be unique per premises.",
    )

    @api.depends("number", "location_id")
    def _compute_is_current(self):
        latest = dict(self.sudo()._read_group(
            [("location_id", "in", self.location_id.ids)], ["location_id"], ["number:max"],
        ))
        for version in self:
            version.is_current = latest.get(version.location_id) == version.number

    @api.depends("name")
    def _compute_url(self):
        # get_base_url() takes one record; several versions are computed together (e.g. sending pending ones).
        for version in self:
            version.url = f"{version.get_base_url()}/cjenik/{quote(version.name)}" if version.name else False

    @api.ondelete(at_uninstall=False)
    def _unlink_except_recent(self):
        limit = fields.Datetime.now() - timedelta(days=KEEP_DAYS)
        if any(version.published_at > limit for version in self):
            raise UserError(_(
                "A price list must stay public at least %(days)s days after it was published. "
                "Delete only older versions.",
                days=KEEP_DAYS,
            ))

    @api.model
    def _cron_publish(self):
        locations = self.env["l10n_hr.price.list.location"].sudo().search([])
        for location in locations:
            try:
                with self.env.cr.savepoint():
                    location._publish()
            except UserError as error:
                _logger.warning("Price list not published: %s", error)
            except Exception:
                _logger.exception("Price list %s not published", location.name)
        if self.env.context.get("cron_id"):
            # Versions are saved before anything is sent to a website.
            self.env["ir.cron"]._commit_progress(len(locations), remaining=0)
        locations._send_webhooks()

    @api.model
    def _trigger_publish(self):
        """Check the price lists in a minute (several changes in a row: one check)."""
        data = self.env.cr.precommit.data  # cleared at commit and rollback
        if data.get("l10n_hr_price_list.triggered") or self.env.context.get("l10n_hr_price_list_publishing"):
            return
        if not self.env["l10n_hr.price.list.location"].sudo().search_count([], limit=1):
            return
        cron = self.env.ref("l10n_hr_price_list.ir_cron_price_list_publish", raise_if_not_found=False)
        if cron:
            cron.sudo()._trigger(fields.Datetime.now() + timedelta(minutes=1))
            data["l10n_hr_price_list.triggered"] = True

    # ------------------------------------------------------------------
    # Webhook
    # ------------------------------------------------------------------

    def _webhook_payload(self):
        self.ensure_one()
        return {
            "event": "price_list.published",
            "company": self.company_id.name,
            "company_vat": self.company_id.vat or "",
            "premises": self.location_id.name,
            "premises_label": self.location_id.object_code,
            "number": self.number,
            "file_name": self.name,
            "published_at": local_time(self.published_at).isoformat(),
            "url": self.url,
            "content_type": "text/csv; charset=utf-8",
            "content_base64": self.file.decode(),
            "rows": public_rows(json.loads(self.rows_json)) if self.rows_json else [],
        }

    def _webhook_send(self):
        self.ensure_one()
        location = self.location_id.sudo()
        body = json.dumps(self._webhook_payload(), ensure_ascii=False).encode()
        headers = {"Content-Type": "application/json; charset=utf-8", "User-Agent": "Odoo l10n_hr_price_list"}
        if location.webhook_secret:
            signature = hmac.new(location.webhook_secret.encode(), body, hashlib.sha256).hexdigest()
            headers["X-Price-List-Signature"] = f"sha256={signature}"
        try:
            # No redirects: a redirected POST becomes a GET and its 3xx would look like success.
            response = requests.post(
                location.webhook_url, data=body, headers=headers, timeout=WEBHOOK_TIMEOUT, allow_redirects=False,
            )
            error = None if 200 <= response.status_code < 300 else f"HTTP {response.status_code} {response.reason or ''}".strip()
        except requests.RequestException as exception:
            error = str(exception)
        if error:
            _logger.warning("Price list %s not sent to the webhook: %s", self.name, error)
            self.write({"webhook_state": "error", "webhook_error": error[:500]})
            cron = self.env.ref("l10n_hr_price_list.ir_cron_price_list_publish", raise_if_not_found=False)
            if cron:
                cron.sudo()._trigger(fields.Datetime.now() + timedelta(hours=1))
            return False
        self.write({"webhook_state": "sent", "webhook_error": False, "webhook_sent_at": fields.Datetime.now()})
        return True
