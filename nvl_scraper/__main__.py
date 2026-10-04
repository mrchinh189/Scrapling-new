"""Scrape raw-material (NVL) prices and store them as CSV + Excel.

Usage:
    python -m nvl_scraper                      # all sources -> data/nvl_prices.csv/.xlsx
    python -m nvl_scraper --only mpoc 100ppi_h2so4
    python -m nvl_scraper --list
"""

import argparse
import logging
import sys
from pathlib import Path

from nvl_scraper.sources import SOURCES
from nvl_scraper.storage import merge_into_csv, write_excel

log = logging.getLogger("nvl_scraper")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nvl_scraper", description="Cào giá nguyên vật liệu (NVL)")
    parser.add_argument("--out", default="data", help="Thư mục lưu kết quả (mặc định: data)")
    parser.add_argument("--only", nargs="+", metavar="ID", help="Chỉ chạy các nguồn này")
    parser.add_argument("--list", action="store_true", help="Liệt kê các nguồn rồi thoát")
    parser.add_argument("--no-excel", action="store_true", help="Không xuất file Excel")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    if args.list:
        for src in SOURCES:
            print(f"{src.id:<16} {src.url}")
        return 0

    sources = [s for s in SOURCES if not args.only or s.id in args.only]
    if args.only and len(sources) != len(set(args.only)):
        known = {s.id for s in SOURCES}
        parser.error(f"Nguồn không tồn tại: {sorted(set(args.only) - known)}")

    records, failed = [], []
    for src in sources:
        try:
            got = src.scrape()
            records += got
            latest = max(got, key=lambda r: r.price_date)
            log.info(
                "OK   %-16s %d dòng, mới nhất %s = %s %s",
                src.id,
                len(got),
                latest.price_date,
                latest.price,
                latest.unit,
            )
        except Exception as exc:
            failed.append(src.id)
            log.error("FAIL %-16s %s", src.id, exc, exc_info=args.verbose)

    out = Path(args.out)
    rows, added = merge_into_csv(out / "nvl_prices.csv", records)
    if not args.no_excel:
        write_excel(out / "nvl_prices.xlsx", rows)
    log.info("Đã lưu %d dòng mới (tổng %d) vào %s", added, len(rows), out)

    if failed:
        log.error("Các nguồn lỗi: %s", ", ".join(failed))
    # Non-zero only when everything failed, so one flaky site doesn't block saving the rest
    return 1 if failed and not records else 0


if __name__ == "__main__":
    sys.exit(main())
