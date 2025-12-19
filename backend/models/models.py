from pydantic import BaseModel, HttpUrl, Field, config
from typing import Optional
from datetime import datetime, timezone

class Product(BaseModel):
    id: int
    title: str
    img: Optional[str]
    price: Optional[int]
    sale: bool
    url: str
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    favorite: Optional[bool] = False

class Price_log(BaseModel):
    prod_id: int
    price: int
    sale: bool
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Group(BaseModel):
    name: str
    products: Optional[list] = []