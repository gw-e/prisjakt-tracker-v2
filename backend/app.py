from fastapi import FastAPI, HTTPException, Query, Depends, Path, Body
from scrapers.scraper import scrape_product
from models.models import Product, Price_log
from database import Database
from typing import Optional, List
from pymongo import UpdateOne
import asyncio
from datetime import datetime, timezone

app = FastAPI()
db = Database()

@app.get("/")
async def read_root():
    return "heha"


@app.get("/v1/scrape")
async def scrape(url: str = Query(...)):
    try:
        data = await scrape_product(url)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/product/add")
async def add_product(product: Product):
    existing_product = await db.get_product_by_id(product.id)

    if existing_product:
        raise HTTPException(status_code=409, detail="Product already added!")
    
    product_data = product.model_dump()
    result = await db.insert_product(product_data)

    if product.price is not None:
        price_log = Price_log(
            prod_id=product.id,
            price=product.price,
            sale=product.sale
        )
        await db.insert_price_log(price_log.model_dump())

    return {
        "message": "Product added successfully",
        "inserted_id": str(result)
    }


@app.put("/v1/product/update/{prod_id}")
async def update_prod(prod_id: int = Path(..., description="Product ID to update")):
    existing_product = await db.get_product_by_id(prod_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found!")
    
    url = existing_product["url"]
    scraped = await scrape_product(url)
    if not scraped:
        raise HTTPException(status_code=500, detail="Couldn't scrape product!")
    
    new_data = Product(**scraped).model_dump()
    new_data["last_updated"] = datetime.now(timezone.utc)

    updated = await db.update_product(prod_id, new_data)
    if not updated:
        raise HTTPException(status_code=500, detail="Database update failed")

    price_log = Price_log(
        prod_id=prod_id,
        price=scraped["price"],
        sale=scraped["sale"]
    )
    await db.insert_price_log(price_log.model_dump())

    return {
        "message": "Product updated successfully",
        "product": updated
    }