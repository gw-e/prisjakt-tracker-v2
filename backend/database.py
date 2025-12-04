from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from pymongo import UpdateOne
import os

class Database:
    def __init__(self, uri: str = "mongodb://localhost:27017", db_name: str = "prisjakt-tracker-v2"):
        print(uri)
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.products_collection = self.db["products"]
        # self.price_log_collection = self.db["price_log"]
        # self.groups_collection = self.db["groups"]
    
    async def get_product_by_id(self, id: int):
        return await self.products_collection.find_one({"id": id})
    
    async def insert_product(self, product_data: dict):
        result = await self.products_collection.insert_one(product_data)
        return result.inserted_id