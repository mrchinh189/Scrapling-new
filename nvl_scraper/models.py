from dataclasses import asdict, dataclass, field, fields
from datetime import date, datetime


@dataclass
class PriceRecord:
    """One price observation of a raw material (NVL) from one source."""

    source: str  # source id, e.g. "mpoc"
    material: str  # human-readable material name, e.g. "Dầu cọ thô (CPO)"
    series: str  # contract / quote type, e.g. "Settlement", "Cash", "CPOc1"
    price_date: date
    price: float
    currency: str
    unit: str
    change: float | None = None
    change_pct: float | None = None
    url: str = ""
    scraped_at: datetime = field(default_factory=lambda: datetime.now().replace(microsecond=0))

    @property
    def key(self) -> tuple:
        """Identity used to de-duplicate rows across runs."""
        return self.source, self.material, self.series, self.price_date.isoformat()

    def to_row(self) -> dict:
        row = asdict(self)
        row["price_date"] = self.price_date.isoformat()
        row["scraped_at"] = self.scraped_at.isoformat(sep=" ")
        return row

    @classmethod
    def columns(cls) -> list[str]:
        return [f.name for f in fields(cls)]
