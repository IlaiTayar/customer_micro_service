from pydantic import BaseModel

from model.base_models.customer import Customer
from model.base_models.order import Order


class OrderRequest(BaseModel):
    customer: Customer
    order: Order