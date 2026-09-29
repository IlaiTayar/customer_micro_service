from typing import Optional

from pydantic import BaseModel


class ItemResponse(BaseModel):
    item_id: Optional[int] = None
    seller_id: int
    item_name: str
    price: float