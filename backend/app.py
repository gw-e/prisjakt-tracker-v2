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













@app.post("/v1/product/update")
async def update_product(url: str = Body(..., embed=True)):
    # 1) Scrape product
    scraped = await scrape_product(url)
    prod_id = scraped["id"]

    # 2) Check if product exists
    existing_product = await db.get_product_by_id(prod_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 3) Prepare updated fields
    updated_data = {
        "title": scraped["title"],
        "img": scraped["img"],
        "price": scraped["price"],
        "sale": scraped["sale"],
        "url": scraped["url"],
        "last_updated": datetime.now(timezone.utc)
    }

    # 4) Update product document (even if nothing changed)
    updated_product = await db.update_product(prod_id, updated_data)

    # 5) Log price
    price_log = Price_log(
        prod_id=prod_id,
        price=scraped["price"],
        sale=scraped["sale"]
    )
    await db.insert_price_log(price_log.model_dump())

    return {
        "message": "Product updated successfully",
        "product": updated_product
    }