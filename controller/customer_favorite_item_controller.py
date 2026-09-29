from typing import List, Optional

from fastapi import APIRouter, HTTPException

from model.base_models.customer_favorite_item import CustomerFavoriteItem
from model.requst_response_models.customer_favorite_item_request import CustomerFavoriteItemRequest
from model.requst_response_models.customer_favorite_item_response import CustomerFavoriteItemResponse
from service import customer_favorite_item_service

router: APIRouter = APIRouter(prefix="/customer-favorite-item",
                              tags=["customer-favorite-item"])


@router.post("/create", status_code=201)
async def create_favorite_item(customer_request: CustomerFavoriteItemRequest) -> int:
    result = await customer_favorite_item_service.create_favorite_item(customer_request)
    if result is None:
        raise HTTPException(status_code=404, detail=f"item with name: {customer_request.item_name} not found or customer with id: {customer_request.customer_id} not found")

    return result


@router.put("/update-{favorite_item_id}", status_code=200)
async def update_favorite_item_by_id(favorite_item_id, favorite_item: CustomerFavoriteItem) -> str:
    result = await customer_favorite_item_service.update_favorite_item_by_id(favorite_item_id, favorite_item)
    if result is None:
        raise HTTPException(status_code=404, detail=f"favorite item with id: {favorite_item_id} not found")

    return result


@router.get("/get-item-{favorite_item_id}", response_model=CustomerFavoriteItemResponse, status_code=200)
async def get_favorite_item_by_id(favorite_item_id: int) -> CustomerFavoriteItemResponse:
    result = await customer_favorite_item_service.get_favorite_item_by_id(favorite_item_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"favorite item with id: {favorite_item_id} not found")

    return result


@router.get("/get-customer-{customer_id}")
async def get_favorite_items_by_customer_id(customer_id: int) -> List[CustomerFavoriteItemResponse]:
    result: Optional[List[CustomerFavoriteItemResponse]] = await customer_favorite_item_service.get_favorite_items_by_customer_id(customer_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"customer with id: {customer_id} not found")

    return result


@router.delete("/delete-{favorite_item_id}", status_code=200)
async def delete_favorite_item_by_id(favorite_item_id: int) -> str:
    result = await customer_favorite_item_service.delete_favorite_item_by_id(favorite_item_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"favorite item with id: {favorite_item_id} not found")

    return result