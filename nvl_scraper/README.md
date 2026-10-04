# NVL scraper — cào giá nguyên vật liệu

Module dùng Scrapling để lấy giá nguyên vật liệu từ nhiều nguồn, gộp vào một file lịch sử
CSV và xuất Excel. Chạy tự động mỗi ngày bằng GitHub Actions.

## Các nguồn hiện có

| id | Nguồn | Dữ liệu | Đơn vị | Cách lấy |
|---|---|---|---|---|
| `investing_cpo` | vn.investing.com — Malaysian Crude Palm Oil Futures | Giá khớp gần nhất, thay đổi, % | USD/tấn | HTTP → trình duyệt stealth (Cloudflare) |
| `100ppi_h2so4` | 生意社 100ppi — 硫酸 (axit sunfuric) | Giá tham chiếu ~8 ngày gần nhất, % thay đổi | CNY/tấn | HTTP |
| `mpoc` | MPOC Daily Palm Oil Prices | Giá settlement CPO (~10 phiên) + giá tháng CPO/SBO/SFO | MYR/tấn, USD/tấn | HTTP |
| `lme_zinc` | LME Zinc — Trading summary | Cash & 3-months (Bid/Offer), trễ 1 ngày | USD/tấn | Trình duyệt + bắt API `/api/trading-data` |

## Cài đặt

```bash
pip install -e ".[fetchers]" -r nvl_scraper/requirements.txt
scrapling install          # tải trình duyệt cho StealthyFetcher (Investing, LME)
```

## Chạy

```bash
python -m nvl_scraper                     # tất cả nguồn -> data/nvl_prices.csv + data/nvl_prices.xlsx
python -m nvl_scraper --only mpoc lme_zinc
python -m nvl_scraper --list
python -m nvl_scraper -v                  # log chi tiết khi debug
```

Kết quả:
- `data/nvl_prices.csv` — lịch sử, mỗi dòng là (nguồn, NVL, series, ngày giá). Chạy lại trong ngày
  không tạo dòng trùng; giá bị điều chỉnh sẽ được ghi đè.
- `data/nvl_prices.xlsx` — sheet **Mới nhất** (giá gần nhất của từng series) và **Lịch sử**.

Một nguồn lỗi không làm mất dữ liệu các nguồn khác; lệnh chỉ trả mã lỗi khi tất cả đều lỗi.

## Thêm NVL mới

Sửa `nvl_scraper/sources/__init__.py`:

- Cùng website đã hỗ trợ → thêm 1 dòng, ví dụ:
  ```python
  Ppi100Source("100ppi_naoh", "https://m1.100ppi.com/vane/<id>-<tên>.html", "Xút (NaOH)"),
  InvestingSource("investing_copper", "https://vn.investing.com/commodities/copper", "Đồng (Copper)"),
  LmeSource("lme_aluminium", "https://www.lme.com/en/Metals/Non-ferrous/LME-Aluminium", "Nhôm"),
  ```
- Website mới → tạo class kế thừa `Source` trong `nvl_scraper/sources/`, viết `parse(page)` trả về
  danh sách `PriceRecord`, rồi thêm test với HTML mẫu trong `tests/nvl_scraper/fixtures/`.

## Chạy hằng ngày

`.github/workflows/nvl-prices.yml` chạy 12:07 UTC (19:07 giờ VN) mỗi ngày và có thể bấm chạy tay
(*Actions → NVL prices (daily) → Run workflow*). Workflow commit `data/` vào nhánh mặc định và
đính kèm file làm artifact. Lịch `schedule` của GitHub chỉ chạy trên nhánh mặc định.

Chạy trên máy/server riêng thì dùng cron:

```cron
7 19 * * * cd /path/to/Scrapling-new && python -m nvl_scraper >> nvl.log 2>&1
```

## Lưu ý

- Investing và LME có chống bot; IP datacenter (như GitHub Actions) đôi khi vẫn bị chặn. Khi đó
  chạy trên máy trong nước/văn phòng hoặc dùng proxy.
- LME chỉ công bố công khai giá trễ 1 ngày; lịch sử và giá trung bình tháng cần đăng nhập.
- Kiểm tra điều khoản sử dụng của từng website trước khi dùng dữ liệu cho mục đích thương mại.
