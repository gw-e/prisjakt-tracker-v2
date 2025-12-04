import requests

PRISJAKT_TRACKER_URL = "http://127.0.0.1:8000/"
PRODUCT_URL = "https://www.prisjakt.no/product.php?p=14365093"

res = requests.get(f"{PRISJAKT_TRACKER_URL}/v1/scrape?url={PRODUCT_URL}")
product = res.json()

res = requests.post(f"{PRISJAKT_TRACKER_URL}/v1/product/add", json=product)
print(res.text)