from typing import Optional, List, Union

from model.base_models.customer import Customer, CustomerStatus
from model.exception_handler_model.customer_exception import CustomerException
from repository import customer_repository, order_repository, customer_favorite_item_repository
from notification import notification_service


async def _check_for_vip(customer_status: CustomerStatus) -> Union[List[Customer], CustomerException]:
    vip_customers: List[Customer] = await customer_repository.get_customer_by_status(customer_status)
    if len(vip_customers) >= 10:
        return CustomerException.VIP_MAX_LIMIT

    return vip_customers


async def create_customer(customer: Customer) -> Union[int, CustomerException]:
    existing_customer = await get_customer_by_email(customer.email)

    if existing_customer == CustomerException.CUSTOMER_NOT_FOUND:

        if customer.status == CustomerStatus.VIP:
            if await _check_for_vip(customer.status) == CustomerException.VIP_MAX_LIMIT:
                return CustomerException.VIP_MAX_LIMIT

        return await customer_repository.create_customer(customer)

    return CustomerException.CUSTOMER_EXISTS


async def update_customer_by_id(customer_id: int, customer: Customer) -> Union[str, CustomerException]:
    existing_customer = await customer_repository.get_customer_by_id(customer_id)

    if existing_customer is None:
        return CustomerException.CUSTOMER_NOT_FOUND

    existing_email = await get_customer_by_email(customer.email)
    if isinstance(existing_email, Customer):

        if existing_email.customer_id != customer_id:
            return CustomerException.CUSTOMER_EXISTS

    if existing_customer.status == CustomerStatus.REGULAR and customer.status == CustomerStatus.VIP:
        if await _check_for_vip(customer.status) == CustomerException.VIP_MAX_LIMIT:
            return CustomerException.VIP_MAX_LIMIT

    return await customer_repository.update_customer_by_id(customer_id, customer)


async def get_customer_by_id(customer_id: int) -> Union[Customer, CustomerException]:

    customer: Optional[Customer] = await customer_repository.get_customer_by_id(customer_id)

    if customer is None:
        return CustomerException.CUSTOMER_NOT_FOUND

    return customer


async def get_customer_by_email(customer_email: str) -> Union[Customer, CustomerException]:
    customer: Optional[Customer] = await customer_repository.get_customer_by_email(customer_email)
    if customer is None:
        return CustomerException.CUSTOMER_NOT_FOUND

    return customer


async def get_all_customers() -> List[Customer]:
    return await customer_repository.get_all_customers()


async def delete_customer_by_id(customer_id: int) -> Union[str, CustomerException]:
    existing_customer: Optional[Customer] = await customer_repository.get_customer_by_id(customer_id)
    if not existing_customer:
        return CustomerException.CUSTOMER_NOT_FOUND

    customer_orders = await order_repository.get_orders_by_customer_id(customer_id)
    for order in customer_orders:
        await order_repository.delete_order_by_id(order.order_id)

    customer_favorites = await customer_favorite_item_repository.get_favorite_items_by_customer_id(customer_id)
    for favorite in customer_favorites:
        await customer_favorite_item_repository.delete_favorite_item_by_id(favorite.favorite_item_id)

    if customer_orders or customer_favorites:
        notification_service.notify_customer(
            customer_id,
            f"your account was deleted along with {len(customer_orders)} order(s) and {len(customer_favorites)} favorite item(s)"
        )

    return await customer_repository.delete_customer_by_id(customer_id)