from typing import List, Optional

from pydantic import BaseModel

from model.base_models.customer import Customer
from model.base_models.order import Order


class OrderResponse(BaseModel):
    customer: Optional[Customer] = None
    customer_orders: List[Order] = []