import csv
from playwright.sync_api import sync_playwright

# =============================
# TUOTTEET
# =============================
PRODUCTS = [
    {
        "code": "HLBY-DAMS",
        "name": "HLBY"
    },
    {
        "code": "NSBY-DAMS",
        "name": "NSBY"
    }
]

BASE_URL = "https://live.euronext.com/en/product/commodities-futures/{code}/settlement-prices"


def scrape_product(page, product):
    url = BASE_URL.format(code=product["code"])
    output_file = f"{product['name']}_settlement.csv"

    page.goto(url, timeout=60000)
    page.wait_for_selector("table#DataTables_Table_0", timeout=60000)

    headers = page.locator("table thead th").all_inner_texts()
    rows = page.locator("table tbody tr")

    data = []
    for i in range(rows.count()):
        cells = rows.nth(i).locator("td").all_inner_texts()
        if len(cells) == len(headers):
            data.append(cells)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

    print(f"✅ {product['code']} → {output_file}")


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )
    page = browser.new_page()

    for product in PRODUCTS:
        scrape_product(page, product)

    browser.close()
