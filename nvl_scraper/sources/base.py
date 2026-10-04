from abc import ABC, abstractmethod

from nvl_scraper.fetch import fetch
from nvl_scraper.models import PriceRecord


class Source(ABC):
    """A price source: knows how to fetch its page and turn it into PriceRecords.

    ``parse`` is kept separate from ``scrape`` so it can be unit-tested against
    saved HTML without network access.
    """

    id: str
    url: str
    mode: str = "auto"  # "auto" | "http" | "stealth"
    must_have: str | None = None  # CSS selector proving the page loaded correctly
    capture_xhr: str | None = None

    def scrape(self) -> list[PriceRecord]:
        page = fetch(self.url, mode=self.mode, must_have=self.must_have, capture_xhr=self.capture_xhr)
        return self.parse(page)

    @abstractmethod
    def parse(self, page) -> list[PriceRecord]:
        """Extract records from a Scrapling Response / Selector."""
