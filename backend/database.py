from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from pymongo import UpdateOne, ReturnDocument
import os
from bson import ObjectId

class Database:
    def __init__(self, uri: str = "mongodb://localhost:27017", db_name: str = "prisjakt-tracker-v2"):
        print(uri)
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.products_collection = self.db["products"]
        self.price_log_collection = self.db["price-log"]

    @staticmethod # vatafak is dis man
    def serialize_doc(doc: dict):
            if not doc:
                return doc

            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    doc[key] = str(value)
            return doc
    
    async def get_product_by_id(self, id: int):
        doc = await self.products_collection.find_one({"id": id})
        return Database.serialize_doc(doc) # dont think i need this
    
    async def insert_product(self, product_data: dict):
        result = await self.products_collection.insert_one(product_data)
        return result.inserted_id
    
    async def insert_price_log(self, log_data: dict):
        result = await self.price_log_collection.insert_one(log_data)
        return result.inserted_id



    async def update_product(self, prod_id: int, updated_fields: dict):
        updated = await self.products_collection.find_one_and_update(
            {"id": prod_id},
            {"$set": updated_fields},
            return_document=ReturnDocument.AFTER # wah?
        )

        return Database.serialize_doc(updated)
    

    