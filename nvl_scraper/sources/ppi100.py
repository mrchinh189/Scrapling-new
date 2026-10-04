from datetime import date

from nvl_scraper.models import PriceRecord
from nvl_scraper.sources.base import Source
from nvl_scraper.utils import infer_year, parse_number


class Ppi100Source(Source):
    """生意社 (100ppi.com) mobile "价格走势" page, e.g. /vane/236-硫酸.html.

    The table lists ~8 recent days as (MM-DD, price, daily change %). Prices are
    published before ~14:00 China time; today's row shows "-" until then.
    """

    mode = "auto"
    must_have = "table.tttable"

    def __init__(self, id: str, url: str, material: str, currency: str = "CNY", unit: str = "CNY/tấn"):
        self.id, self.url, self.material, self.currency, self.unit = id, url, material, currency, unit

    def parse(self, page, today: date | None = None) -> list[PriceRecord]:
        records = []
        for row in page.css("table.tttable tr"):
            cells = [c.strip() for c in row.css("td::text").getall()]
            if len(cells) < 3 or "-" not in cells[0] or not cells[0][:2].isdigit():
                continue  # header row or unexpected layout
            price = parse_number(cells[1])
            if price is None:
                continue  # not published yet
            month, day = map(int, cells[0].split("-"))
            records.append(
                PriceRecord(
                    source=self.id,
                    material=self.material,
                    series="Giá tham chiếu 生意社",
                    price_date=infer_year(month, day, today),
                    price=price,
                    currency=self.currency,
                    unit=self.unit,
                    change_pct=parse_number(cells[2]),
                    url=self.url,
                )
            )
        if not records:
            raise ValueError("100ppi: no price rows found")
        return records
