from pydantic import BaseModel


class FavoriteItemLookupByNameRequest(BaseModel):
    customer_id: int
    item_name: str


class FavoriteItemLookupByIdRequest(BaseModel):
    customer_id: int
    item_id: int
