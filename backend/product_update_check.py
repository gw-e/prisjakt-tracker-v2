import asyncio
import httpx
from datetime import datetime, timezone


async def product_update_interval(on=True):
    if not on:
        return
    
    url = "http://127.0.0.1:8000"

    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(f"{url}/v1/products")
                products = response.json()
                not_updated = _not_updated_products(products)
                
                if not not_updated:
                    pass

                for prod in not_updated:
                    response = await client.put(f"{url}/v1/product/update/{prod["id"]}")


            except Exception as e:
                print(f"Error: {e}")

            await asyncio.sleep(30)


def _not_updated_products(products):
    current_date = datetime.now(timezone.utc)
    update_interval = 24
    result = []

    for prod in products:
        last_updated = datetime.fromisoformat(prod["last_updated"])
        
        if last_updated.tzinfo is None:
            product_date = last_updated.replace(tzinfo=timezone.utc)

        diff = current_date - product_date
        hours = diff.total_seconds() / 3600

        if hours >= update_interval:
            result.append(prod)

    return result