from typing import Optional, List, Union

from api.internal_api.seller_service import seller_service_api
from model.base_models.customer import Customer
from model.base_models.order import Order
from model.exception_handler_model.customer_exception import CustomerException
from model.exception_handler_model.order_exception import OrderException
from model.requst_response_models.order_request import OrderRequest
from model.requst_response_models.order_response import OrderResponse
from repository import order_repository
from service import customer_service



async def create_order(order_request: OrderRequest) -> Union[OrderResponse, CustomerException, OrderException]:
    selected_customer: Customer
    if order_request.customer.customer_id is None:
        created_customer_id: Union[int, CustomerException] = await customer_service.create_customer(order_request.customer)

        if isinstance(created_customer_id, CustomerException):
            return created_customer_id

        customer: Union[Customer, CustomerException] = await customer_service.get_customer_by_id(created_customer_id)

        if isinstance(customer, CustomerException):
            return customer

    else:
        existing_customer: Union[Customer, CustomerException] = await customer_service.get_customer_by_id(order_request.customer.customer_id)
        if isinstance(existing_customer, CustomerException):
            return existing_customer

        customer: Customer = existing_customer

    selected_customer = customer
    order_request.order.customer_id = selected_customer.customer_id

    seller_item = await seller_service_api.get_lowest_price_item_by_name(order_request.order.item_name)
    if seller_item is not None:
        order_request.order.price = seller_item.price

    await order_repository.create_order(order_request.order)
    customer_orders = await order_repository.get_orders_by_customer_id(selected_customer.customer_id)
    order_response: OrderResponse = OrderResponse(customer=selected_customer, customer_orders=customer_orders)

    return order_response


async def update_order_by_id(order_id: int, order: Order) -> Union[str, OrderException]:
    existing_order: Union[Order, OrderException] = await get_order_by_id(order_id)
    if isinstance(existing_order, OrderException):
        return existing_order

    if order.order_id is not None and order.order_id != existing_order.order_id:
        return OrderException.INVALID_INPUT

    if order.customer_id is not None and order.customer_id != existing_order.customer_id:
        return OrderException.INVALID_INPUT

    seller_item = await seller_service_api.get_lowest_price_item_by_name(order.item_name)
    if seller_item is not None:
        order.price = seller_item.price

    return await order_repository.update_order_by_id(order_id, order)


async def get_order_by_id(order_id: int) -> Union[Order, OrderException]:
    order: Optional[Order] = await order_repository.get_order_by_id(order_id)

    if not order:
        return OrderException.ORDER_NOT_FOUND

    return order


async def get_orders_by_customer_id(customer_id: int) -> Union[List[Order], CustomerException]:
    customer: Union[Customer, CustomerException] = await customer_service.get_customer_by_id(customer_id)

    if isinstance(customer, CustomerException):
        return customer

    return await order_repository.get_orders_by_customer_id(customer_id)


async def get_all_orders() -> List[Order]:

    return await order_repository.get_all_orders()


async def delete_order_by_id(order_id: int) -> Union[str, OrderException]:
    order: Union[Order, OrderException] = await get_order_by_id(order_id)

    if isinstance(order, OrderException):
        return order

    return await order_repository.delete_order_by_id(order_id)