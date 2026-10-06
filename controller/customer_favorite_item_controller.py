from typing import Any, Union

from fastapi import APIRouter, Depends, HTTPException, Query

from model.base_models.customer_favorite_item import CustomerFavoriteItem
from model.exception_handler_model.customer_exception import CustomerException
from model.exception_handler_model.favorite_item_exception import FavoriteItemException
from model.requst_response_models.customer_favorite_item_request import CustomerFavoriteItemRequest
from model.requst_response_models.customer_favorite_item_response import CustomerFavoriteItemResponse
from model.requst_response_models.customer_favorites_response import CustomerFavoritesResponse
from model.requst_response_models.favorite_item_lookup_request import (
    FavoriteItemLookupByIdRequest,
    FavoriteItemLookupByNameRequest,
)
from security.auth import Principal, get_current_principal, require_ownership
from security.internal_auth import verify_internal_api_key
from service import customer_favorite_item_service

router: APIRouter = APIRouter(prefix="/customer-favorite-item",
                              tags=["customer-favorite-item"])


def _exception_handler(result: Any) -> Any:
    if isinstance(result, CustomerException) or isinstance(result, FavoriteItemException):

        if result == CustomerException.CUSTOMER_NOT_FOUND:
            raise HTTPException(status_code=404, detail=f"{CustomerException.CUSTOMER_NOT_FOUND}")

        if result == FavoriteItemException.FAVORITE_ITEM_NOT_FOUND:
            raise HTTPException(status_code=404, detail=f"{FavoriteItemException.FAVORITE_ITEM_NOT_FOUND}")

        if result == FavoriteItemException.FAVORITE_ITEM_ALREADY_EXISTS:
            raise HTTPException(status_code=409, detail=f"{FavoriteItemException.FAVORITE_ITEM_ALREADY_EXISTS}")

        if result == FavoriteItemException.SOMTHING_WENT_WRONG:
            raise HTTPException(status_code=500, detail=f"{FavoriteItemException.SOMTHING_WENT_WRONG}")

    return result


@router.post("", status_code=201)
async def create_favorite_item(customer_request: CustomerFavoriteItemRequest, principal: Principal = Depends(get_current_principal)) -> int:
    require_ownership(principal, customer_request.customer_id)

    result: Union[int, CustomerException, FavoriteItemException] = await customer_favorite_item_service.create_favorite_item(customer_request)

    final_result = _exception_handler(result)

    return final_result


@router.get("", response_model=CustomerFavoritesResponse, status_code=200)
async def get_favorite_items_by_customer_id(customer_id: int = Query(...)) -> CustomerFavoritesResponse:
    result: Union[CustomerFavoritesResponse, CustomerException] = await customer_favorite_item_service.get_favorite_items_by_customer_id(customer_id)

    final_result = _exception_handler(result)

    return final_result


@router.get("/references", status_code=200, dependencies=[Depends(verify_internal_api_key)])
async def count_favorites_by_item_id(item_id: int = Query(...)) -> int:
    return await customer_favorite_item_service.count_favorites_by_item_id(item_id)


@router.post("/lookup/by-name", response_model=CustomerFavoriteItemResponse, status_code=200)
async def lookup_item_by_name_and_favorite(lookup_request: FavoriteItemLookupByNameRequest, principal: Principal = Depends(get_current_principal)) -> CustomerFavoriteItemResponse:
    require_ownership(principal, lookup_request.customer_id)

    result: Union[CustomerFavoriteItemResponse, CustomerException, FavoriteItemException] = await customer_favorite_item_service.lookup_item_by_name_and_favorite(lookup_request.customer_id, lookup_request.item_name)

    final_result = _exception_handler(result)

    return final_result


@router.post("/lookup/by-id", response_model=CustomerFavoriteItemResponse, status_code=200)
async def lookup_item_by_id_and_favorite(lookup_request: FavoriteItemLookupByIdRequest, principal: Principal = Depends(get_current_principal)) -> CustomerFavoriteItemResponse:
    require_ownership(principal, lookup_request.customer_id)

    result: Union[CustomerFavoriteItemResponse, CustomerException, FavoriteItemException] = await customer_favorite_item_service.lookup_item_by_id_and_favorite(lookup_request.customer_id, lookup_request.item_id)

    final_result = _exception_handler(result)

    return final_result


@router.get("/{favorite_item_id}", response_model=CustomerFavoriteItemResponse, status_code=200)
async def get_favorite_item_by_id(favorite_item_id: int) -> CustomerFavoriteItemResponse:
    result: Union[CustomerFavoriteItemResponse, FavoriteItemException] = await customer_favorite_item_service.get_favorite_item_by_id(favorite_item_id)

    final_result = _exception_handler(result)

    return final_result


@router.put("/{favorite_item_id}", status_code=200)
async def update_favorite_item_by_id(favorite_item_id: int, favorite_item: CustomerFavoriteItem, principal: Principal = Depends(get_current_principal)) -> str:
    existing_favorite: Union[CustomerFavoriteItemResponse, FavoriteItemException] = await customer_favorite_item_service.get_favorite_item_by_id(favorite_item_id)
    existing_favorite = _exception_handler(existing_favorite)
    require_ownership(principal, existing_favorite.customer_id)

    favorite_item.customer_id = principal.principal_id

    result: Union[str, FavoriteItemException, CustomerException] = await customer_favorite_item_service.update_favorite_item_by_id(favorite_item_id, favorite_item)

    final_result = _exception_handler(result)

    return final_result


@router.delete("/{favorite_item_id}", status_code=200)
async def delete_favorite_item_by_id(favorite_item_id: int, principal: Principal = Depends(get_current_principal)) -> str:
    existing_favorite: Union[CustomerFavoriteItemResponse, FavoriteItemException] = await customer_favorite_item_service.get_favorite_item_by_id(favorite_item_id)
    existing_favorite = _exception_handler(existing_favorite)
    require_ownership(principal, existing_favorite.customer_id)

    result: Union[str, FavoriteItemException] = await customer_favorite_item_service.delete_favorite_item_by_id(favorite_item_id)

    final_result = _exception_handler(result)

    return final_result
