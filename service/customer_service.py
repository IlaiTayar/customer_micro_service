from typing import Optional, List

from model.base_models.customer import Customer, CustomerStatus
from repository import customer_repository, order_repository


async def _check_for_vip(customer_status: CustomerStatus):
    vip_customers: List[Customer] = await customer_repository.get_customer_by_status(customer_status)
    if len(vip_customers) >= 10:
        return "MAXED"

    return vip_customers


async def create_customer(customer: Customer) -> Optional[int]:

    if customer.status == CustomerStatus.VIP:
        if await _check_for_vip(customer.status) == "MAXED":
            return None

    return await customer_repository.create_customer(customer)


async def update_customer_by_id(customer_id: int, customer: Customer) -> Optional[str]:
    existing_customer: Optional[Customer] = await customer_repository.get_customer_by_id(customer_id)

    if not existing_customer:
        return None

    if existing_customer.status == CustomerStatus.REGULAR and customer.status == CustomerStatus.VIP:
        if await _check_for_vip(customer.status) == "MAXED":
            return "MAXED"

    return await customer_repository.update_customer_by_id(customer_id, customer)


async def get_customer_by_id(customer_id: Optional[int]) -> Optional[Customer]:
    if not customer_id:
        return None

    customer: Optional[Customer] = await customer_repository.get_customer_by_id(customer_id)

    if not customer:
        return None

    return customer


async def get_all_customers() -> List[Customer]:
    return await customer_repository.get_all_customers()


async def delete_customer_by_id(customer_id: int) -> Optional[str]:
    existing_customer: Optional[Customer] = await customer_repository.get_customer_by_id(customer_id)
    if not existing_customer:
        return None

    customer_orders = await order_repository.get_orders_by_customer_id(customer_id)
    for order in customer_orders:
        order_id = order.order_id
        await order_repository.delete_order_by_id(order_id)

    return await customer_repository.delete_customer_by_id(customer_id)