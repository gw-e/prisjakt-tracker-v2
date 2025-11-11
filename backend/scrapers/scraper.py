import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

def scrape_product(url: str): #async def
    with httpx.Client() as client: #async with, .AsyncClient()
        headers = {"User-Agent": "Mozilla/5.0"}
        response = client.get(url, headers=headers) #await client.
        response.raise_for_status()
        html = response.text

    soup = BeautifulSoup(html, 'html.parser')

    prod_title = _get_prod_title(soup)
    prod_img = _get_prod_img(soup)
    prod_price = _get_prod_price(soup)
    prod_sale = _get_prod_sale(soup)

    return {
        "title": prod_title,
        "img": prod_img,
        "price": prod_price,
        "sale": prod_sale
    }

def _get_prod_title(soup):
    title_element = soup.find('h1', class_='Text--q06h0j iYVnhg h2text StyledDesktopTitle-sc-1naplf-2 dpwvdE')
    if not title_element:
        raise Exception("Title not found")
    return title_element.text.strip()

def _get_prod_img(soup):
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        return og_image["content"]
    return None

def _get_prod_price(soup):
    price_element = soup.find('h4', class_='Text--q06h0j gxjLMM h4text StyledPriceLabel-sc-1iq0wa2-2 coORKe')
    if not price_element:
        raise Exception("Price not found")
    raw_price = price_element.text.strip()
    cleaned_price = ''.join(filter(str.isdigit, raw_price))
    return int(cleaned_price)

def _get_prod_sale(soup):
    sale_element = soup.find('span', class_='Text--q06h0j ftkWDj StyledText--2v1apx beZcjd')
    return bool(sale_element)



if __name__ == "__main__":
    prod = scrape_product("https://www.prisjakt.no/product.php?p=14022090")
    print(prod)
