from typing import Optional

from pydantic import BaseModel


class CustomerFavoriteItemRequest(BaseModel):
    favorite_item_id: Optional[int] = None
    customer_id: int
    item_name: str