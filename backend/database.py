from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from pymongo import UpdateOne, ReturnDocument
import os
from bson import ObjectId

class Database:
    def __init__(self, uri: str = "mongodb://localhost:27017", db_name: str = "prisjakt-tracker-v2"):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.products_collection = self.db["products"]
        self.price_log_collection = self.db["price-log"]
        self.groups_collection = self.db["groups"]


    async def get_product_by_id(self, id: int):
        return await self.products_collection.find_one({"id": id}, {"_id": 0})
    
    async def get_group_by_name(self, name: str):
        return await self.groups_collection.find_one({"name": name}, {"_id": 0})
    
    async def insert_product(self, product_data: dict):
        result = await self.products_collection.insert_one(product_data)
        return result.inserted_id
    
    async def insert_price_log(self, log_data: dict):
        result = await self.price_log_collection.insert_one(log_data)
        return result.inserted_id

    async def insert_group(self, group_data: dict):
        result = await self.groups_collection.insert_one(group_data)
        return result.inserted_id
    
    async def update_product(self, prod_id: int, updated_fields: dict):
        return await self.products_collection.find_one_and_update(
            {"id": prod_id},
            {"$set": updated_fields},
            return_document=ReturnDocument.AFTER,
            projection={"_id": 0}
        )
    
    # async def update_favorite_product(self, prod_id: int, new_data: bool):
    #     return
    
    async def update_group(self, name: str, new_data: dict):
        result = await self.groups_collection.update_one(
            {"name": name},
            {"$set": new_data}
        )
        return result.modified_count
    
    async def remove_group(self, name: str):
        group_result = await self.groups_collection.delete_one({"name": name})
        return group_result.deleted_count
    

    