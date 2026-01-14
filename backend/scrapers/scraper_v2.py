import requests
from bs4 import BeautifulSoup
import re
import json

def scrape_v2(url):
    data = _fetch_prefetch_json(url)
    prod_data = data["data"]["product"]
    
    prod_id = prod_data["id"]
    prod_name = prod_data["name"]
    prod_img = prod_data["media"]["first"]
    prod_price = prod_data["priceSummary"]["regular"]
    prod_sale = bool(prod_data["dealInfo"])
    prod_discount = prod_data["dealInfo"]["dealPercentage"] if prod_sale else None
    prod_stock_status = prod_data["stockStatus"].replace("_", " ")
    
    prod_properties = prod_data["coreProperties"]["nodes"]
    if prod_properties:
        prod_props = []
        for prop in prod_properties:
            prod_props.append(prop["prettyVerbose"])
        prod_properties = prod_props

    prod_stores = _get_prod_stores(prod_data["prices"]["nodes"])  

    return {
        "id": prod_id,
        "name": prod_name,
        "img": prod_img,
        "url": url,
        "price": prod_price,
        "sale": prod_sale,
        "discount": prod_discount,
        "stock": prod_stock_status,
        "properties": prod_properties,
        "stores": prod_stores
    }


def _fetch_prefetch_json(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    script_tag = soup.find("script", attrs={"data-script": "globals"})
    if not script_tag or not script_tag.string:
        raise RuntimeError("Globals script not found")

    script = script_tag.string

    match = re.search(
        r"window\.PREFETCH\s*=\s*JSON\.parse\('(.+?)'\);",
        script,
        re.DOTALL
    )

    if not match:
        raise RuntimeError("PREFETCH JSON not found")

    json_string = match.group(1)

    json_string = json_string.encode("utf-8").decode("unicode_escape").replace('\xa0', " ")

    return json.loads(json_string)


def _get_prod_stores(stores_data):
    stores = []

    if not stores_data:
        return stores

    for store in stores_data:
        if store["condition"] != "new":
            continue

        current_price = store["price"]["exclShipping"]
        offer = store["offerPrices"]
        original = offer["originalPrice"]

        on_sale = original is not None

        if on_sale:
            original_price = original["exclShipping"]
            discount_percent = round(
                (original_price - current_price) / original_price * 100, 1
            )
        else:
            original_price = None
            discount_percent = 0

        dict_store = {
            "store": store["store"]["name"],
            "prod_name": store["name"],
            "url": store["externalUri"],
            "price": current_price,
            "on_sale": on_sale,
            "original_price": original_price,
            "discount_percent": discount_percent,
            "stock": store["stock"]["status"].replace("_", " "),
            "availability": store["availability"]["availabilityDate"]
        }

        stores.append(dict_store)

    return stores



# if __name__ == "__main__":
#     result = scrape_v2("https://www.prisjakt.no/product.php?p=13622516")
