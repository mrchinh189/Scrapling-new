from nvl_scraper.sources.base import Source
from nvl_scraper.sources.investing import InvestingSource
from nvl_scraper.sources.lme import LmeSource
from nvl_scraper.sources.mpoc import MpocSource
from nvl_scraper.sources.ppi100 import Ppi100Source

# Add new materials here. Same-site pages reuse the same class with another URL,
# e.g. another 100ppi product: Ppi100Source("100ppi_xut", "https://m1.100ppi.com/vane/<id>-<name>.html", "Xút (NaOH)")
SOURCES: list[Source] = [
    InvestingSource(
        id="investing_cpo",
        url="https://vn.investing.com/commodities/malaysian-crude-palm-oil-futures-streaming-chart",
        material="Dầu cọ thô (CPO) futures",
    ),
    Ppi100Source(
        id="100ppi_h2so4",
        url="https://m1.100ppi.com/vane/236-%E7%A1%AB%E9%85%B8.html",
        material="Axit sunfuric (H2SO4)",
    ),
    MpocSource(),
    LmeSource(
        id="lme_zinc",
        url="https://www.lme.com/en/Metals/Non-ferrous/LME-Zinc",
        material="Kẽm (Zinc)",
    ),
]

__all__ = ["SOURCES", "Source", "InvestingSource", "LmeSource", "MpocSource", "Ppi100Source"]
