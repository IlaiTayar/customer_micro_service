from pydantic import BaseModel

from model.base_models.customer import Customer


class OrderRequest(BaseModel):
    customer: Customer
    item_name: str


class OrderUpdateRequest(BaseModel):
    item_name: str
