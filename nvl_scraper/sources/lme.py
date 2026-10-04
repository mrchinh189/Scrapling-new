import json
import logging
import re
from datetime import date, datetime

from nvl_scraper.models import PriceRecord
from nvl_scraper.sources.base import Source
from nvl_scraper.utils import parse_number

log = logging.getLogger(__name__)

_WANTED = re.compile(r"^(cash|3[- ]?months?)$", re.I)


class LmeSource(Source):
    """LME metal page (e.g. LME-Zinc), "Trading summary" table (day-delayed, US$/t).

    The table is filled by JavaScript from ``/api/trading-data/...``, so this source
    always uses the browser and captures that API call. If the JSON layout is not
    recognised it falls back to the rendered HTML table.
    """

    mode = "stealth"
    capture_xhr = r"https://www\.lme\.com/api/trading-data/.*"

    def __init__(self, id: str, url: str, material: str):
        self.id, self.url, self.material = id, url, material

    def parse(self, page) -> list[PriceRecord]:
        records = []
        for xhr in getattr(page, "captured_xhr", None) or []:
            try:
                records += self.parse_api(json.loads(xhr.body))
            except (ValueError, TypeError, KeyError) as exc:
                log.debug("LME: skip XHR %s: %s", xhr.url, exc)
        if not records:
            records = self.parse_table(page)
        if not records:
            raise ValueError("LME: trading summary not found (page layout or API changed?)")
        # The page may fire the same API call more than once
        return list({r.key: r for r in records}.values())

    def parse_api(self, data: dict) -> list[PriceRecord]:
        price_date = _to_date(data.get("DateOfData")) or date.today()
        out = []
        for row in data.get("Rows") or []:
            label = str(row.get("Label", "")).strip()
            values = row.get("Values") or []
            if _WANTED.match(label) and values:
                out += self._records(label, values, price_date)
        return out

    def parse_table(self, page) -> list[PriceRecord]:
        out = []
        for tr in page.css("table tr"):
            cells = [" ".join(c.get_all_text().split()) for c in tr.css("th, td")]
            if len(cells) >= 2 and _WANTED.match(cells[0]):
                out += self._records(cells[0], cells[1:3], date.today())
        return out

    def _records(self, label: str, values: list, price_date: date) -> list[PriceRecord]:
        label = "3-months" if label.lower().startswith("3") else "Cash"
        out = []
        for side, value in zip(("Bid", "Offer"), values):
            price = parse_number(value)
            if price is not None:
                out.append(
                    PriceRecord(
                        source=self.id,
                        material=self.material,
                        series=f"{label} {side}",
                        price_date=price_date,
                        price=price,
                        currency="USD",
                        unit="USD/tấn",
                        url=self.url,
                    )
                )
        return out


def _to_date(value) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        return None
