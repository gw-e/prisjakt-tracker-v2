from pydantic import BaseModel, HttpUrl, Field, config
from typing import Optional
from datetime import datetime, timezone

class Product(BaseModel):
    id: int
    name: str
    img: Optional[str]
    url: str
    price: Optional[int]
    sale: bool
    discount: Optional[int]
    stock: Optional[str]
    properties: Optional[list]
    stores: Optional[list] = []
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    favorite: Optional[bool] = False

class Price_log(BaseModel):
    prod_id: int
    price: Optional[int]
    sale: Optional[bool]
    current_store: Optional[str]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Group(BaseModel):
    name: str
    products: Optional[list] = []