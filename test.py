import requests

BASE = "http://127.0.0.1:8000"
PRODUCT_URL = "https://www.prisjakt.no/product.php?p=14365093"

# 1) Scrape
r = requests.get(f"{BASE}/v1/scrape", params={"url": PRODUCT_URL})
product = r.json()
print("Scraped:", product)

# 2) Add (ignore 409)
r = requests.post(f"{BASE}/v1/product/add", json=product)
print("Add:", r.status_code, r.text)

# 1) Update the product
r = requests.post(
    f"{BASE}/v1/product/update",
    json={"url": PRODUCT_URL}      # <-- important: Body(..., embed=True)
)
print("Status:", r.status_code)
print("Response:", r.json())