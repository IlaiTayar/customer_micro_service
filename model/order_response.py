from typing import List, Optional

from pydantic import BaseModel

from model.customer import Customer
from model.order import Order


class OrderResponse(BaseModel):
    customer: Optional[Customer] = None
    customer_orders: List[Order] = []