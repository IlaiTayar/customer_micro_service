from typing import List, Any, Union

from fastapi import APIRouter, HTTPException, Query

from model.base_models.order import Order
from model.exception_handler_model.customer_exception import CustomerException
from model.exception_handler_model.order_exception import OrderException
from model.requst_response_models.order_request import OrderRequest, OrderUpdateRequest
from model.requst_response_models.order_response import OrderResponse
from service import order_service

router = APIRouter(
    prefix="/order",
    tags=["order"]
)


def _exception_handler(result: Any) -> Any:
    if isinstance(result, (OrderException, CustomerException)):
        if result == CustomerException.CUSTOMER_NOT_FOUND:
            raise HTTPException(status_code=404, detail=f"{result.name}")

        if result == CustomerException.CUSTOMER_EXISTS:
            raise HTTPException(status_code=409, detail=f"{result.name}")

        if result == CustomerException.VIP_MAX_LIMIT:
            raise HTTPException(status_code=409, detail=f"{result.name}")

        if result == OrderException.ORDER_NOT_FOUND:
            raise HTTPException(status_code=404, detail=f"{result.name}")

        if result == OrderException.ORDER_ALREADY_EXISTS:
            raise HTTPException(status_code=409, detail=f"{result.name}")

        if result == OrderException.INVALID_INPUT:
            raise HTTPException(status_code=422, detail=f"{result.name}")

        if result == OrderException.ITEM_NOT_FOUND:
            raise HTTPException(status_code=404, detail=f"{result.name}")

    return result


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(order_request: OrderRequest) -> OrderResponse:
    result = await order_service.create_order(order_request)
    return _exception_handler(result)


@router.get("/references", status_code=200)
async def count_orders_by_item_id(item_id: int = Query(...)) -> int:
    return await order_service.count_orders_by_item_id(item_id)


@router.get("/id/{order_id}", response_model=Order, status_code=200)
async def get_order_by_id(order_id: int) -> Order:
    result = await order_service.get_order_by_id(order_id)
    return _exception_handler(result)


@router.get("/{customer_id}", response_model=List[Order], status_code=200)
async def get_orders_by_customer_id(customer_id: int) -> List[Order]:
    result = await order_service.get_orders_by_customer_id(customer_id)
    return _exception_handler(result)


@router.put("/{order_id}", status_code=200)
async def update_order_by_id(order_id: int, order: OrderUpdateRequest) -> str:
    result = await order_service.update_order_by_id(order_id, order)
    return _exception_handler(result)


@router.delete("/{order_id}", status_code=200)
async def delete_order_by_id(order_id: int) -> str:
    result = await order_service.delete_order_by_id(order_id)
    return _exception_handler(result)
