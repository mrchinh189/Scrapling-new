from datetime import date, datetime

from nvl_scraper.models import PriceRecord
from nvl_scraper.sources.base import Source
from nvl_scraper.utils import parse_number


class InvestingSource(Source):
    """Any Investing.com instrument page (commodities, futures...).

    The site is behind Cloudflare, so ``auto`` mode usually escalates to the browser.
    """

    mode = "auto"
    must_have = '[data-test="instrument-price-last"]'

    def __init__(self, id: str, url: str, material: str, currency: str = "USD", unit: str = "USD/tấn"):
        self.id, self.url, self.material, self.currency, self.unit = id, url, material, currency, unit

    def parse(self, page) -> list[PriceRecord]:
        price = parse_number(page.css('[data-test="instrument-price-last"]::text').get())
        if price is None:
            raise ValueError("Investing: last price not found")

        # Use the trading-time label when present (last session date), else today
        price_date = date.today()
        stamp = page.css('time[data-test="trading-time-label"]::attr(datetime)').get()
        if stamp:
            price_date = datetime.fromisoformat(stamp.replace("Z", "+00:00")).date()

        title = page.css("h1::text").get("") or ""
        series = title[title.rfind("(") + 1 : title.rfind(")")] if "(" in title else "Last"

        return [
            PriceRecord(
                source=self.id,
                material=self.material,
                series=series,
                price_date=price_date,
                price=price,
                currency=self.currency,
                unit=self.unit,
                change=parse_number(page.css('[data-test="instrument-price-change"]::text').get()),
                change_pct=parse_number(page.css('[data-test="instrument-price-change-percent"]::text').get()),
                url=self.url,
            )
        ]
