from typing import Optional, List, Union

from model.base_models.customer import Customer, CustomerStatus
from model.exception_handler_model.customer_exception import CustomerException
from repository import customer_repository, order_repository


async def _check_for_vip(customer_status: CustomerStatus):
    vip_customers: List[Customer] = await customer_repository.get_customer_by_status(customer_status)
    if len(vip_customers) >= 10:
        return CustomerException.VIP_MAX_LIMIT

    return vip_customers


async def create_customer(customer: Customer) -> Union[int, CustomerException]:
    existing_mails = await customer_repository.get_customer_by_email(customer.email)
    if len(existing_mails) > 0:
        return CustomerException.CUSTOMER_EXISTS

    if customer.status == CustomerStatus.VIP:
        if await _check_for_vip(customer.status) == CustomerException.VIP_MAX_LIMIT:
            return CustomerException.VIP_MAX_LIMIT

    return await customer_repository.create_customer(customer)


async def update_customer_by_id(customer_id: int, customer: Customer) -> Union[str, CustomerException]:
    existing_customer: Optional[Customer] = await customer_repository.get_customer_by_id(customer_id)

    if not existing_customer:
        return CustomerException.CUSTOMER_NOT_FOUND

    existing_mails = await customer_repository.get_customer_by_email(customer.email)
    if len(existing_mails) > 0:
        for mail in existing_mails:
            if mail.customer_id != customer_id and mail.email == customer.email:
                return CustomerException.CUSTOMER_EXISTS

    if existing_customer.status == CustomerStatus.REGULAR and customer.status == CustomerStatus.VIP:
        if await _check_for_vip(customer.status) == CustomerException.VIP_MAX_LIMIT:
            return CustomerException.VIP_MAX_LIMIT

    return await customer_repository.update_customer_by_id(customer_id, customer)


async def get_customer_by_id(customer_id: int) -> Union[Customer, CustomerException]:

    customer: Optional[Customer] = await customer_repository.get_customer_by_id(customer_id)

    if not customer:
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
        order_id = order.order_id
        await order_repository.delete_order_by_id(order_id)

    return await customer_repository.delete_customer_by_id(customer_id)