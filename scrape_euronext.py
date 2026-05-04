import csv
from playwright.sync_api import sync_playwright

URL = "https://live.euronext.com/en/product/commodities-futures/HLBY-DAMS/settlement-prices"
OUTPUT = "HLBY_settlement.csv"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )
    page = browser.new_page()

    page.goto(URL, timeout=60000)
    page.wait_for_selector("table#DataTables_Table_0", timeout=60000)

    headers = page.locator("table thead th").all_inner_texts()
    rows = page.locator("table tbody tr")

    data = []
    for i in range(rows.count()):
        cells = rows.nth(i).locator("td").all_inner_texts()
        if len(cells) == len(headers):
            data.append(cells)

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

    browser.close()

print(f"✅ CSV valmis: {OUTPUT}")
