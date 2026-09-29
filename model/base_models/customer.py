from enum import Enum
from typing import Optional

from pydantic import BaseModel


class CustomerStatus(Enum):
    REGULAR = "REGULAR"
    VIP = "VIP"


class Customer(BaseModel):
    customer_id: Optional[int] = None
    first_name: str
    last_name: str
    email: str
    status: CustomerStatus = CustomerStatus.REGULAR