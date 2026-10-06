from typing import List, Any, Union

from fastapi import APIRouter, Depends, HTTPException, Query

from model.base_models.order import Order
from model.exception_handler_model.customer_exception import CustomerException
from model.exception_handler_model.order_exception import OrderException
from model.requst_response_models.order_request import OrderRequest
from model.requst_response_models.order_response import OrderResponse
from security.auth import Principal, get_current_principal, require_ownership
from security.internal_auth import verify_internal_api_key
from service import order_service

router = APIRouter(
    prefix="/order",
    tags=["order"]
)


def _exception_handler(result:Any) -> Any :
    if isinstance(result, OrderException) or isinstance(result, CustomerException):
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
async def create_order(order_request: OrderRequest, principal: Principal = Depends(get_current_principal)) -> OrderResponse:

    order_request.customer.customer_id = principal.principal_id
    order_request.order.customer_id = principal.principal_id

    result: Union[OrderResponse, OrderException, CustomerException] = await order_service.create_order(order_request)

    final_result = _exception_handler(result)

    return final_result


@router.get("", response_model=List[Order], status_code=200)
async def get_all_orders() -> List[Order]:

    return await order_service.get_all_orders()


@router.get("/references", status_code=200, dependencies=[Depends(verify_internal_api_key)])
async def count_orders_by_item_id(item_id: int = Query(...)) -> int:
    return await order_service.count_orders_by_item_id(item_id)


@router.get("/{order_id}", response_model=Order, status_code=200)
async def get_order_by_id(order_id: int) -> Order:
    result: Union[Order, OrderException, CustomerException] = await order_service.get_order_by_id(order_id)

    final_result = _exception_handler(result)

    return final_result


@router.put("/{order_id}", status_code=200)
async def update_order_by_id(order_id: int, order: Order, principal: Principal = Depends(get_current_principal)) -> str:

    existing_order: Union[Order, OrderException, CustomerException] = await order_service.get_order_by_id(order_id)
    existing_order = _exception_handler(existing_order)
    require_ownership(principal, existing_order.customer_id)

    order.customer_id = principal.principal_id

    result: Union[str, OrderException, CustomerException] = await order_service.update_order_by_id(order_id, order)

    final_result = _exception_handler(result)

    return final_result


@router.delete("/{order_id}", status_code=200)
async def delete_order_by_id(order_id: int, principal: Principal = Depends(get_current_principal)) -> str:
    existing_order: Union[Order, OrderException, CustomerException] = await order_service.get_order_by_id(order_id)
    existing_order = _exception_handler(existing_order)
    require_ownership(principal, existing_order.customer_id)

    result: Union[str, OrderException, CustomerException] = await order_service.delete_order_by_id(order_id)

    final_result = _exception_handler(result)

    return final_result
