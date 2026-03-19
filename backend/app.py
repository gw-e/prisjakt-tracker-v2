from fastapi import FastAPI, HTTPException, Query, Depends, Path, Body, Request, Form
from scrapers.scraper import scrape_product
from scrapers.scraper_v2 import scrape_v2
from models.models import Product, Price_log, Group
from database import Database
from product_update_check import product_update_interval
from typing import Optional, List
from pymongo import UpdateOne
import asyncio
from datetime import datetime, timezone
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(product_update_interval(False))
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)
db = Database()

template = Jinja2Templates(directory="../frontend/templates")

app.mount(
    "/static",
    StaticFiles(directory="../frontend/static"),
    name="static",
)

@app.get("/")
async def on_load():
    return RedirectResponse(url="/home", status_code=HTTP_303_SEE_OTHER)

@app.get("/home")
async def page_home(request: Request):
    products = await db.get_all_products()
    return template.TemplateResponse(
        "home.html", 
        {
            "request": request,
            "products": products,
        }
    )

@app.get("/add-product")
async def page_add_product(request: Request):
    return template.TemplateResponse(
        "add-product.html",
        {
            "request": request,
            "header": "Add Product",
        }
    )


@app.get("/v1/scrape")
async def scrape(url: str = Query(...)):
    try:
        data = await scrape_product(url)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v2/scrape")
async def scrape_product_v2(url: str = Query(...)):
    try:
        data = await scrape_v2(url)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/product/{prod_id}/get")
async def get_product(prod_id: int):
    product = await db.get_product_by_id(prod_id)
    return product

@app.get("/v1/products")
async def get_products():
    return await db.get_all_products()

@app.get("/v1/product/favorites")
async def get_favorites():
    favorites = await db.get_favorite_products()
    return favorites


@app.get("/v1/product/sales")
async def get_products_on_sale():
    sales = await db.get_all_products_on_sale()
    return sales


@app.post("/v1/product/add")
async def add_product(product: Product):
    existing_product = await db.get_product_by_id(product.id)

    if existing_product:
        raise HTTPException(status_code=409, detail="Product already added!")
    
    product_data = product.model_dump()
    result = await db.insert_product(product_data)

    price_log = Price_log(
        prod_id=product.id,
        price=product.price,
        sale=product.sale,
        current_store=product.stores[0]["store"] if len(product.stores) != 0 else None
    )
    await db.insert_price_log(price_log.model_dump())

    return {
        "message": "Product added successfully",
        "inserted_id": str(result)
    }


@app.post("/v2/product/add")
async def add_product(add_data: dict):
    if not "url" in add_data:
        raise HTTPException(status_code=422, detail="Missing url!")
    
    url = add_data["url"]
    scraped = await scrape_product_v2(url)
    if not scraped:
        raise HTTPException(status_code=500, detail="Couldn't scrape product!")
    
    product = Product(**scraped)

    existing_product = await db.get_product_by_id(product.id)

    if existing_product:
        raise HTTPException(status_code=409, detail="Product already added!")
    
    product_data = product.model_dump()
    result = await db.insert_product(product_data)

    price_log = Price_log(
        prod_id=product.id,
        price=product.price,
        sale=product.sale,
        current_store=product.stores[0]["store"] if len(product.stores) != 0 else None
    )
    await db.insert_price_log(price_log.model_dump())

    return {
        "message": "Product added successfully",
        "inserted_id": str(result),
        "product_id": product.id
    }


@app.post("/v3/product/add")
async def add_product(request: Request, url: str = Form(...)):
    scraped = await scrape_product_v2(url)
    if not scraped:
        raise HTTPException(status_code=500, detail="Couldn't scrape product!")
    
    product = Product(**scraped)

    existing_product = await db.get_product_by_id(product.id)
    if existing_product:
        raise HTTPException(status_code=409, detail="Product already added!")
    
    # product_data = product.model_dump()
    result = await db.insert_product(product.model_dump())

    price_log = Price_log(
        prod_id=product.id,
        price=product.price,
        sale=product.sale,
        current_store=product.stores[0]["store"] if len(product.stores) != 0 else None
    )
    await db.insert_price_log(price_log.model_dump())

    referer = request.headers.get("referer", "/")
    return RedirectResponse(url=referer, status_code=HTTP_303_SEE_OTHER)


@app.put("/v1/product/update/{prod_id}")
async def update_prod(prod_id: int = Path(..., description="Product ID to update")):
    existing_product = await db.get_product_by_id(prod_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found!")
    
    url = existing_product["url"]
    scraped = await scrape_product_v2(url)
    if not scraped:
        raise HTTPException(status_code=500, detail="Couldn't scrape product!")
    
    preserved_fields = {
        "favorite": existing_product.get("favorite", False)
    }

    new_data = Product(**scraped, **preserved_fields).model_dump()
    new_data["last_updated"] = datetime.now(timezone.utc)

    updated = await db.update_product(prod_id, new_data)
    if not updated:
        raise HTTPException(status_code=500, detail="Database update failed")

    price_log = Price_log(
        prod_id=prod_id,
        price=scraped["price"],
        sale=scraped["sale"],
        current_store=scraped["stores"][0]["store"] if len(scraped["stores"]) != 0 else None
    )
    await db.insert_price_log(price_log.model_dump())

    return {
        "message": "Product updated successfully",
        "product": updated
    }


@app.put("/v1/product/{prod_id}/favorite/toggle")
async def favorite_product(prod_id: int):
    existing_product = await db.get_product_by_id(prod_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found!")
    
    if not existing_product["favorite"]:
        new_data = True
    else:
        new_data = False

    updated = await db.update_product(prod_id, {"favorite": new_data})

    return {
        "message": "Product updated successfully",
        "product": updated
    }


@app.post("/v1/group/new")
async def new_group(group: Group):
    existing_group = await db.get_group_by_name(group.name)

    if existing_group:
        raise HTTPException(status_code=409, detail="Group already added!")
    
    group_data = group.model_dump()
    result = await db.insert_group(group_data)

    return {
        "message": "Group added successfully",
        "inserted_id": str(result)
    }


@app.put("/v1/group/{group_name}/add")
async def add_prod_to_group(group_name: str, products: List[int]):
    existing_group = await db.get_group_by_name(group_name)
    if not existing_group:
        raise HTTPException(status_code=404, detail="Group does not exist!")
    
    for prod_id in products:
        product = await db.get_product_by_id(prod_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {prod_id} does not exist")
        
    current_product_ids = existing_group.get("products", [])
    updated_product_ids = list(set(current_product_ids + products))

    await db.update_group(group_name, {"products": updated_product_ids})

    return {
        "message": f"Added {len(products)} product(s) to group '{group_name}'",
        "updated_products": updated_product_ids
    }


@app.put("/v1/group/{group_name}/remove")
async def remove_prod_from_group(group_name: str, products: List[int]):
    existing_group = await db.get_group_by_name(group_name)
    if not existing_group:
        raise HTTPException(status_code=404, detail="Group does not exist!")

    current_product_ids = existing_group.get("products", [])

    updated_product_ids = [pid for pid in current_product_ids if pid not in products]

    await db.update_group(group_name, {"products": updated_product_ids})

    return {
        "message": f"Removed {len(products)} product(s) from group '{group_name}'",
        "updated_products": updated_product_ids
    }


@app.put("/v1/group/{group_name}/edit")
async def edit_group(group_name: str, new_data: Group):
    existing_group = await db.get_group_by_name(group_name)
    if not existing_group:
        raise HTTPException(status_code=404, detail="Group does not exist!")

    if new_data.name != group_name:
        if await db.get_group_by_name(new_data.name):
            raise HTTPException(status_code=409, detail="A group with the new name already exists!")
        
    update_data = new_data.model_dump(exclude_unset=True)
    updated_count = await db.update_group(group_name, update_data)

    return {
        "message": f"Group '{group_name}' updated successfully",
        "updated_count": updated_count
    }


@app.delete("/v1/group/{group_name}/delete")
async def delete_group(group_name: str):
    existing_group = await db.get_group_by_name(group_name)
    if not existing_group:
        raise HTTPException(status_code=404, detail="Group does not exist!")

    deleted_group_count = await db.remove_group(group_name)

    return {
        "message": "Group removed successfully",
        "deleted_group_count": deleted_group_count,
    }


@app.delete("/v1/product/{prod_id}/delete")
async def delete_product(prod_id: int):
    existing_product = await db.get_product_by_id(prod_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found!")

    deleted_product_count = await db.remove_product(prod_id)
    deleted_price_logs_count = await db.remove_price_logs_for_product(prod_id)
    updated_groups_count = await db.remove_product_from_all_groups(prod_id)

    return {
        "message": "Product deleted successfully",
        "deleted_product_count": deleted_product_count,
        "deleted_price_logs_count": deleted_price_logs_count,
        "groups_updated": updated_groups_count,
    }