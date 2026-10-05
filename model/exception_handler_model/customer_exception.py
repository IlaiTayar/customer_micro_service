from enum import Enum


class CustomerException(Enum):
    CUSTOMER_NOT_FOUND = "CUSTOMER NOT FOUND"
    CUSTOMER_EXISTS = "CUSTOMER EXISTS"
    VIP_MAX_LIMIT = "VIP MAX LIMIT"
