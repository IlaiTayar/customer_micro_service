from typing import Optional, List

from model.customer import Customer
from model.order import Order
from model.order_request import OrderRequest
from model.order_response import OrderResponse
from repository import order_repository, customer_repository
from service import customer_service



async def create_order(order_request: OrderRequest) -> Optional[OrderResponse]:
    selected_customer: Customer

    if order_request.customer.customer_id is None:
        created_customer_id = await customer_service.create_customer(order_request.customer)
        customer = await customer_repository.get_customer_by_id(created_customer_id)
        if created_customer_id is None or customer is None:
            return None

    else:
        existing_customer: Optional[Customer] = await customer_service.get_customer_by_id(order_request.customer.customer_id)
        if not existing_customer:
            return None
        customer = existing_customer

    selected_customer = customer
    order_request.order.customer_id = selected_customer.customer_id

    await order_repository.create_order(order_request.order)
    customer_orders = await order_repository.get_orders_by_customer_id(selected_customer.customer_id)
    order_response: OrderResponse = OrderResponse(customer=selected_customer, customer_orders=customer_orders)

    return order_response


async def update_order_by_id(order_id: int, order: Order) -> Optional[str]:
    existing_order: Optional[Order] = await order_repository.get_order_by_id(order_id)

    if not existing_order:
        return None

    return await order_repository.update_order_by_id(order_id, order)


async def get_order_by_id(order_id: int) -> Optional[Order]:
    order: Optional[Order] = await order_repository.get_order_by_id(order_id)

    if not order:
        return None

    return order


async def get_orders_by_customer_id(customer_id: int) -> Optional[List[Order]]:
    customer: Optional[Customer] = await customer_service.get_customer_by_id(customer_id)

    if not customer:
        return None

    return await order_repository.get_orders_by_customer_id(customer_id)


async def get_all_orders() -> List[Order]:

    return await order_repository.get_all_orders()


async def delete_order_by_id(order_id: int) -> Optional[str]:
    order: Optional[Order] = await order_repository.get_order_by_id(order_id)

    if not order:
        return None

    return await order_repository.delete_order_by_id(order_id)