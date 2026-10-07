from typing import Optional

from pydantic import BaseModel

from api.internal_api.seller_service.model.item_response import ItemResponse
from model.base_models.customer import Customer


class CustomerFavoriteItemResponse(BaseModel):
    favorite_item_id: Optional[int] = None
    customer: Customer
    item_response: ItemResponse