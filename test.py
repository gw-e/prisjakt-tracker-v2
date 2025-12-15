import requests

BASE = "http://127.0.0.1:8000"
PRODUCT_URL = "https://www.prisjakt.no/product.php?p=14365093"


def test_update_v2():
    print("\n---- SCRAPING ----")
    r = requests.get(f"{BASE}/v1/scrape", params={"url": PRODUCT_URL})
    scraped = r.json()
    print("Scraped:", scraped)

    print("\n---- ADD PRODUCT ----")
    add = requests.post(f"{BASE}/v1/product/add", json=scraped)
    print("Add:", add.status_code, add.text)

    prod_id = scraped["id"]

    print("\n---- UPDATE PRODUCT ----")
    r = requests.put(f"{BASE}/v1/product/update/{prod_id}")
    print("Status:", r.status_code)
    print("Response:", r.json())

    print("\n---- ADD GROUP ----")
    add = requests.post(f"{BASE}/v1/group/new", json={"name": "test group"})
    print("Add:", add.status_code, add.text)


if __name__ == "__main__":
    test_update_v2()