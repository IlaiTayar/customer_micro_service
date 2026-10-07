from pydantic import BaseModel


class FavoriteItemUpdateRequest(BaseModel):
    item_name: str
