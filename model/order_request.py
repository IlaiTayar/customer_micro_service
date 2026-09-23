from pydantic import BaseModel

from model.customer import Customer
from model.order import Order


class OrderRequest(BaseModel):
    customer: Customer
    order: Order