from typing import List, Optional

from pydantic import BaseModel

from api.internal_api.seller_service.model.item_response import ItemResponse
from model.base_models.customer import Customer


class FavoriteItemEntry(BaseModel):
    favorite_item_id: Optional[int] = None
    item_response: ItemResponse


class CustomerFavoritesResponse(BaseModel):
    customer: Customer
    favorite_items: List[FavoriteItemEntry]
