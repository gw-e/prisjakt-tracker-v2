from fastapi import FastAPI, HTTPException, Query, Depends, Path
from scrapers.scraper import scrape_product
from models.models import Product
from database import Database
from typing import Optional, List
from pymongo import UpdateOne
import asyncio

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

    return {
        "message": "Product added successfully",
        "inserted_id": str(result)
    }