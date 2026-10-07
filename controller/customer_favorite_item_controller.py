from typing import Any, Union

from fastapi import APIRouter, HTTPException, Query

from model.exception_handler_model.customer_exception import CustomerException
from model.exception_handler_model.favorite_item_exception import FavoriteItemException
from model.requst_response_models.customer_favorite_item_request import CustomerFavoriteItemRequest
from model.requst_response_models.customer_favorite_item_response import CustomerFavoriteItemResponse
from model.requst_response_models.customer_favorites_response import CustomerFavoritesResponse
from model.requst_response_models.favorite_item_update_request import FavoriteItemUpdateRequest
from service import customer_favorite_item_service

router: APIRouter = APIRouter(
    prefix="/customer-favorite-item",
    tags=["customer-favorite-item"]
)


def _exception_handler(result: Any) -> Any:
    if isinstance(result, (CustomerException, FavoriteItemException)):
        if result == CustomerException.CUSTOMER_NOT_FOUND:
            raise HTTPException(status_code=404, detail=f"{result}")

        if result == FavoriteItemException.FAVORITE_ITEM_NOT_FOUND:
            raise HTTPException(status_code=404, detail=f"{result}")

        if result == FavoriteItemException.ITEM_NOT_FOUND:
            raise HTTPException(status_code=404, detail=f"{result}")

        if result == FavoriteItemException.ITEM_NOT_IN_FAVORITES:
            raise HTTPException(status_code=404, detail=f"{result}")

        if result == FavoriteItemException.FAVORITE_ITEM_ALREADY_EXISTS:
            raise HTTPException(status_code=409, detail=f"{result}")

        if result == FavoriteItemException.SOMTHING_WENT_WRONG:
            raise HTTPException(status_code=500, detail=f"{result}")

    return result


@router.post("", response_model=CustomerFavoriteItemResponse, status_code=201)
async def create_favorite_item(
    customer_request: CustomerFavoriteItemRequest
) -> CustomerFavoriteItemResponse:
    result = await customer_favorite_item_service.create_favorite_item(customer_request)
    return _exception_handler(result)


@router.get("", response_model=CustomerFavoritesResponse, status_code=200)
async def get_favorite_items_by_customer_id(
    customer_id: int = Query(...)
) -> CustomerFavoritesResponse:
    result = await customer_favorite_item_service.get_favorite_items_by_customer_id(customer_id)
    return _exception_handler(result)


@router.get("/references", status_code=200)
async def count_favorites_by_item_id(item_id: int = Query(...)) -> int:
    return await customer_favorite_item_service.count_favorites_by_item_id(item_id)


@router.post("/lookup/by-name", response_model=CustomerFavoriteItemResponse, status_code=200)
async def lookup_item_by_name(
    customer_request: CustomerFavoriteItemRequest
) -> CustomerFavoriteItemResponse:
    result = await customer_favorite_item_service.lookup_item_by_name(customer_request)
    return _exception_handler(result)


@router.get("/{favorite_item_id}", response_model=CustomerFavoriteItemResponse, status_code=200)
async def get_favorite_item_by_id(favorite_item_id: int) -> CustomerFavoriteItemResponse:
    result = await customer_favorite_item_service.get_favorite_item_by_id(favorite_item_id)
    return _exception_handler(result)


@router.put("/{favorite_item_id}", response_model=CustomerFavoriteItemResponse, status_code=200)
async def update_favorite_item_by_id(
    favorite_item_id: int,
    favorite_item_request: FavoriteItemUpdateRequest
) -> CustomerFavoriteItemResponse:
    result = await customer_favorite_item_service.update_favorite_item_by_id(
        favorite_item_id,
        favorite_item_request
    )
    return _exception_handler(result)


@router.delete("/{favorite_item_id}", status_code=200)
async def delete_favorite_item_by_id(favorite_item_id: int) -> str:
    result = await customer_favorite_item_service.delete_favorite_item_by_id(favorite_item_id)
    return _exception_handler(result)
