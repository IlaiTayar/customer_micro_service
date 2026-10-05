from typing import List, Any, Union

from fastapi import APIRouter, HTTPException

from model.base_models.order import Order
from model.exception_handler_model.customer_exception import CustomerException
from model.exception_handler_model.order_exception import OrderException
from model.requst_response_models.order_request import OrderRequest
from model.requst_response_models.order_response import OrderResponse
from service import order_service

router = APIRouter(
    prefix="/order",
    tags=["order"]
)


def _exception_handler(result:Any) -> Any :
    if isinstance(result, OrderException) or isinstance(result, CustomerException):
        if result == CustomerException.CUSTOMER_NOT_FOUND:
            raise HTTPException(status_code=404, detail=f"{CustomerException.CUSTOMER_NOT_FOUND}")

        if result == OrderException.ORDER_NOT_FOUND:
            raise HTTPException(status_code=404, detail=f"{OrderException.ORDER_NOT_FOUND}")

        if result == OrderException.ORDER_ALREADY_EXISTS:
            raise HTTPException(status_code=409, detail=f"{OrderException.ORDER_ALREADY_EXISTS}")

        if result == OrderException.INVALID_INPUT:
            raise HTTPException(status_code=422, detail=f"{OrderException.INVALID_INPUT}")

    return result



@router.post("/create", response_model=OrderResponse ,status_code=201)
async def create_order(order_request: OrderRequest) -> OrderResponse:

    result: Union[OrderResponse, OrderException, CustomerException] = await order_service.create_order(order_request)

    final_result = _exception_handler(result)

    return final_result


@router.put("/update-{order_id}", status_code=200)
async def update_order_by_id(order_id: int, order: Order) -> str:

    result: Union[str, OrderException, CustomerException] = await order_service.update_order_by_id(order_id, order)

    final_result = _exception_handler(result)

    return final_result


@router.get("/get-{order_id}", response_model=Order ,status_code=200)
async def get_order_by_id(order_id: int) -> Order:
    result: Union[Order, OrderException, CustomerException] = await order_service.get_order_by_id(order_id)

    final_result = _exception_handler(result)

    return final_result


@router.get("/get/all", response_model=List[Order],status_code=200)
async def get_all_orders() -> List[Order]:

    return await order_service.get_all_orders()


@router.delete("/delete-{order_id}", status_code=200)
async def delete_order_by_id(order_id: int) -> str:
    result: Union[str, OrderException, CustomerException] = await order_service.delete_order_by_id(order_id)

    final_result = _exception_handler(result)

    return final_result