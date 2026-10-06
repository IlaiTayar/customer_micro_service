from typing import Optional
from pydantic import BaseModel

class Order(BaseModel):
    order_id: Optional[int] = None
    customer_id: Optional[int] = None
    item_id: Optional[int] = None
    item_name: str
    price: Optional[float] = None
    image_url: Optional[str] = None
