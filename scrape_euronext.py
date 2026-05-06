import csv
from datetime import datetime
from playwright.sync_api import sync_playwright

# =============================
# TUOTTEET
# =============================
PRODUCTS = [
    {"code": "HLBY-DAMS", "name": "HLBY"},
    {"code": "HLBQ-DAMS", "name": "HLBQ"},
    {"code": "HLBM-DAMS", "name": "HLBM"},
    {"code": "NSBY-DAMS", "name": "NSBY"},
    {"code": "NSBQ-DAMS", "name": "NSBQ"},
    {"code": "NSBM-DAMS", "name": "NSBM"},
]

BASE_URL = "https://live.euronext.com/en/product/commodities-futures/{code}/settlement-prices"


# =============================
# PRODUCTCODE
# =============================
def build_product_code(product, delivery):
    if not delivery:
        return None

    d = delivery.strip()

    if d.lower() == "total":
        return None

    parts = d.split()

    year = parts[-1]
    yy = year[-2:]

    if len(parts) == 1:
        return f"{product}-{yy}"

    first = parts[0].upper()

    if first.startswith("Q"):
        return f"{product}{first[1]}-{yy}"

    return f"{product}{first}-{yy}"


# =============================
# SCRAPE
# =============================
def scrape_all():
    all_rows = []
    headers = None

    # 📅 päivän leima
    today = (datetime.utcnow().strftime("%Y-%m-%d"))
    



    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page()

        for product in PRODUCTS:
            url = BASE_URL.format(code=product["code"])
            product_name = product["name"]

            page.goto(url, timeout=60000)
            page.wait_for_selector("table#DataTables_Table_0", timeout=60000)

            if headers is None:
                headers = page.locator("table thead th").all_inner_texts()
                headers.extend(["Product", "ProductCode", "LoadDate"])

            rows = page.locator("table tbody tr")

            for i in range(rows.count()):
                cells = rows.nth(i).locator("td").all_inner_texts()

                if len(cells) < 1:
                    continue

                delivery = cells[0].strip() if cells[0] else ""

                # ❌ SKIPATAAN TOTAL-RIVIT
                if delivery.lower() == "Total" or delivery == "":
                    continue

                product_code = build_product_code(product_name, delivery)

                row = cells + [product_name, product_code, today]
                all_rows.append(row)

        browser.close()

    with open("data/combined_settlement.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(all_rows)

    print("✅ combined_settlement.csv created (no totals + date included)")


if __name__ == "__main__":
    scrape_all()
