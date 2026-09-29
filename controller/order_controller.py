from typing import List, Optional

from fastapi import APIRouter, HTTPException

from model.base_models.order import Order
from model.requst_response_models.order_request import OrderRequest
from model.requst_response_models.order_response import OrderResponse
from service import order_service

router = APIRouter(
    prefix="/order",
    tags=["order"]
)


@router.post("/create", response_model=OrderResponse ,status_code=201)
async def create_order(order_request: OrderRequest) -> OrderResponse:

    result: Optional[OrderResponse] = await order_service.create_order(order_request)
    if result is None:
        raise HTTPException(status_code=409, detail=f"""Cannot creat VIP customer - out of 10 customers limit."""
                                                    f""" /or customer id - out of range for COLUMN customer_id.""")

    return result


@router.put("/update-{order_id}", status_code=200)
async def update_order_by_id(order_id: int, order: Order) -> str:

    result: Optional[str] = await order_service.update_order_by_id(order_id, order)
    if not result:
        raise HTTPException(status_code=404, detail=f"Order with id: {order_id} not found")

    return result


@router.get("/get-{order_id}", response_model=Order ,status_code=200)
async def get_order_by_id(order_id: int) -> Order:
    result: Optional[Order] = await order_service.get_order_by_id(order_id)

    if not result:
        raise HTTPException(status_code=404, detail=f"Order with id: {order_id} not found")

    return result


@router.get("/get/all", response_model=List[Order],status_code=200)
async def get_all_orders() -> List[Order]:

    return await order_service.get_all_orders()


@router.delete("/delete-{order_id}", status_code=200)
async def delete_order_by_id(order_id: int) -> str:
    result: Optional[str] = await order_service.delete_order_by_id(order_id)

    if not result:
        raise HTTPException(status_code=404, detail=f"Order with id: {order_id} not found")

    return result