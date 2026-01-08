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
    
    async def get_favorite_products(self):
        favorites = self.products_collection.find({"favorite": True}, {"_id": 0})
        favorites = await favorites.to_list(1000)
        return favorites
    
    async def get_all_products_on_sale(self):
        on_sale = self.products_collection.find({"sale": True}, {"_id": 0})
        on_sale = await on_sale.to_list(1000)
        return on_sale
    
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
    
    async def update_group(self, name: str, new_data: dict):
        result = await self.groups_collection.update_one(
            {"name": name},
            {"$set": new_data}
        )
        return result.modified_count
    
    async def remove_product_from_all_groups(self, prod_id: int):
        result = await self.groups_collection.update_many(
            {"products": prod_id},
            {"$pull": {"products": prod_id}}
        )
        return result.modified_count
    
    async def remove_group(self, name: str):
        group_result = await self.groups_collection.delete_one({"name": name})
        return group_result.deleted_count
    
    async def remove_product(self, prod_id: int):
        result = await self.products_collection.delete_one({"id": prod_id})
        return result.deleted_count
    
    async def remove_price_logs_for_product(self, prod_id: int):
        result = await self.price_log_collection.delete_many({"prod_id": prod_id})
        return result.deleted_count

    