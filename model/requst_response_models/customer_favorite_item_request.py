from pydantic import BaseModel


class CustomerFavoriteItemRequest(BaseModel):
    customer_id: int
    item_name: str
