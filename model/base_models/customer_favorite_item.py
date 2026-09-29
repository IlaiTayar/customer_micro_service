from typing import Optional

from pydantic import BaseModel


class CustomerFavoriteItem(BaseModel):
    favorite_item_id: Optional[int] = None
    customer_id: int
    item_id: int