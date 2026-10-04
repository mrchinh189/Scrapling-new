from nvl_scraper.models import PriceRecord
from nvl_scraper.sources.base import Source
from nvl_scraper.utils import parse_date, parse_number


class MpocSource(Source):
    """MPOC "Daily Palm Oil Prices".

    Two tables on the page:
      1. CPO settlement price (RM/tonne) for the last ~10 trading days.
      2. Monthly CPO / SBO / SFO prices in US$/MT (date like "26-Jan").
    """

    id = "mpoc"
    url = "https://www.mpoc.org.my/market-insight/daily-palm-oil-prices/"
    mode = "auto"
    must_have = "table"

    def parse(self, page) -> list[PriceRecord]:
        records = []
        for table in page.css("table"):
            headers = [" ".join(h.get_all_text().split()) for h in table.css("th")]
            rows = [[" ".join(td.get_all_text().split()) for td in tr.css("td")] for tr in table.css("tr")]
            rows = [r for r in rows if r]
            if headers and headers[0].lower().startswith("pricing date"):
                records += self._settlement(rows)
            elif headers and headers[0].lower() == "date" and len(headers) >= 4:
                records += self._monthly(headers, rows)
        if not records:
            raise ValueError("MPOC: no price tables found")
        return records

    def _settlement(self, rows) -> list[PriceRecord]:
        out = []
        for cells in rows:
            price = parse_number(cells[1]) if len(cells) > 1 else None
            if price is None:
                continue
            out.append(
                PriceRecord(
                    source=self.id,
                    material="Dầu cọ thô (CPO)",
                    series="Bursa settlement",
                    price_date=parse_date(cells[0], ("%d %b %y", "%d %b %Y")),
                    price=price,
                    currency="MYR",
                    unit="MYR/tấn",
                    url=self.url,
                )
            )
        return out

    def _monthly(self, headers, rows) -> list[PriceRecord]:
        # Only the first three price columns are prices; the rest are premiums
        products = {1: "Dầu cọ thô (CPO)", 2: "Dầu đậu nành (SBO)", 3: "Dầu hướng dương (SFO)"}
        out = []
        for cells in rows:
            if len(cells) < 4:
                continue
            period = parse_date(cells[0], ("%y-%b", "%b-%y"))  # "26-Jan" -> 2026-01-01
            for idx, material in products.items():
                price = parse_number(cells[idx])
                if price is None:
                    continue
                out.append(
                    PriceRecord(
                        source=self.id,
                        material=material,
                        series=f"Monthly {headers[idx]}",
                        price_date=period,
                        price=price,
                        currency="USD",
                        unit="USD/tấn",
                        url=self.url,
                    )
                )
        return out
