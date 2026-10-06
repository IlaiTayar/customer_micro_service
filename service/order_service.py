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
    customer: Customer
    seller_item = await (seller_service_api.get_item_by_item_id(order_request.order.item_id) if order_request.order.item_id is not None else seller_service_api.find_lowest_price_item_by_name(order_request.order.item_name))
    if seller_item is None: return OrderException.ITEM_NOT_FOUND
    if order_request.customer.customer_id is None:
        existing_customer = await customer_service.get_customer_by_email(order_request.customer.email)
        if isinstance(existing_customer, Customer): customer = existing_customer
        elif existing_customer == CustomerException.CUSTOMER_NOT_FOUND:
            created_customer_id = await customer_service.create_customer(order_request.customer)
            if isinstance(created_customer_id, CustomerException): return created_customer_id
            customer_result = await customer_service.get_customer_by_id(created_customer_id)
            if isinstance(customer_result, CustomerException): return customer_result
            customer = customer_result
    else:
        existing_customer = await customer_service.get_customer_by_id(order_request.customer.customer_id)
        if isinstance(existing_customer, CustomerException): return existing_customer
        customer = existing_customer
        customer_by_email = await customer_service.get_customer_by_email(order_request.customer.email)
        if isinstance(customer_by_email, Customer) and customer_by_email.customer_id != customer.customer_id: return CustomerException.CUSTOMER_EXISTS
    order_request.order.customer_id = customer.customer_id
    order_request.order.item_id = seller_item.item_id
    order_request.order.item_name = seller_item.item_name
    order_request.order.price = seller_item.price
    order_request.order.image_url = seller_item.image_url
    await order_repository.create_order(order_request.order)
    customer_orders = await get_orders_by_customer_id(customer.customer_id)
    if isinstance(customer_orders, CustomerException): return customer_orders
    return OrderResponse(customer=customer, customer_orders=customer_orders)

async def update_order_by_id(order_id: int, order: Order) -> Union[str, OrderException]:
    existing = await get_order_by_id(order_id)
    if isinstance(existing, OrderException): return existing
    if order.order_id is not None and order.order_id != existing.order_id: return OrderException.INVALID_INPUT
    if order.customer_id is not None and order.customer_id != existing.customer_id: return OrderException.INVALID_INPUT
    seller_item = await (seller_service_api.get_item_by_item_id(order.item_id) if order.item_id is not None else seller_service_api.find_lowest_price_item_by_name(order.item_name))
    if seller_item is None: return OrderException.ITEM_NOT_FOUND
    order.item_id, order.item_name, order.price, order.image_url = seller_item.item_id, seller_item.item_name, seller_item.price, seller_item.image_url
    return await order_repository.update_order_by_id(order_id, order)

async def get_order_by_id(order_id: int) -> Union[Order, OrderException]:
    order = await order_repository.get_order_by_id(order_id)
    return order if order else OrderException.ORDER_NOT_FOUND

async def get_orders_by_customer_id(customer_id: int) -> Union[List[Order], CustomerException]:
    customer = await customer_service.get_customer_by_id(customer_id)
    if isinstance(customer, CustomerException): return customer
    return await order_repository.get_orders_by_customer_id(customer_id)

async def get_all_orders() -> List[Order]: return await order_repository.get_all_orders()
async def delete_order_by_id(order_id: int) -> Union[str, OrderException]:
    order = await get_order_by_id(order_id)
    if isinstance(order, OrderException): return order
    return await order_repository.delete_order_by_id(order_id)
async def count_orders_by_item_id(item_id: int) -> int:
    return await order_repository.count_orders_by_item_id(item_id)
