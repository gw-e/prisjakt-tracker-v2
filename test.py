import requests

BASE = "http://127.0.0.1:8000"
PRODUCT_URL = "https://www.prisjakt.no/product.php?p=14364107"


def test():
    print("\n---- SCRAPING ----")
    r = requests.get(f"{BASE}/v1/scrape", params={"url": PRODUCT_URL})
    scraped = r.json()
    print("Scraped:", scraped)

    prod_id = scraped["id"]

    print("\n---- ADD PRODUCT ----")
    add = requests.post(f"{BASE}/v1/product/add", json=scraped)
    print("Add:", add.status_code, add.text)

    # print("\n---- GET PRODUCT ----")
    # get = requests.get(f"{BASE}/v1/product/{prod_id}/get")
    # print("Get:", get.status_code, get.text)

    # print("\n---- GET FAVORITE PRODUCT ----")
    # get = requests.get(f"{BASE}/v1/product/favorites")
    # print("Get:", get.status_code, get.text)

    print("\n---- GET PRODUCTS ON SALE ----")
    get = requests.get(f"{BASE}/v1/product/sales")
    print("Get:", get.status_code, get.text)

    # print("\n---- UPDATE PRODUCT ----")
    # r = requests.put(f"{BASE}/v1/product/update/{prod_id}")
    # print("Status:", r.status_code)
    # print("Response:", r.json())

    # print("\n---- FAVORITE PRODUCT ----")
    # r = requests.put(f"{BASE}/v1/product/{prod_id}/favorite/toggle")
    # print("Status:", r.status_code)
    # print("Response:", r.json())

    # print("\n---- DELETE PRODUCT ----")
    # delete = requests.delete(f"{BASE}/v1/product/{prod_id}/delete")
    # print("Delete:", delete.status_code, delete.text)

    # print("\n---- NEW GROUP ----")
    # add = requests.post(f"{BASE}/v1/group/new", json={"name": "test3"})
    # print("Add:", add.status_code, add.text)

    # print("\n---- UPDATE GROUP - ADD ----")
    # group_name = "test2"
    # r = requests.put(f"{BASE}/v1/group/{group_name}/add", json=[14365071])
    # print("Status:", r.status_code)
    # print("Response:", r.json())

    # print("\n---- UPDATE GROUP - REMOVE ----")
    # group_name = "test1"
    # r = requests.put(f"{BASE}/v1/group/{group_name}/remove", json=[14365093, 12406805])
    # print("Status:", r.status_code)
    # print("Response:", r.json())

    # print("\n---- EDIT GROUP ----")
    # group_name = "test1"
    # r = requests.put(f"{BASE}/v1/group/{group_name}/edit", json={"name": "Test"})
    # print("Status:", r.status_code)
    # print("Response:", r.json())

    # print("\n---- DELETE GROUP ----")
    # group_name = "test1"
    # delete = requests.delete(f"{BASE}/v1/group/{group_name}/delete")
    # print("Delete:", delete.status_code, delete.text)


if __name__ == "__main__":
    test()