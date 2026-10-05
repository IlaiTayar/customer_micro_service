from typing import List, Optional, Any, Union

from fastapi import APIRouter, HTTPException

from model.base_models.customer_favorite_item import CustomerFavoriteItem
from model.exception_handler_model.customer_exception import CustomerException
from model.exception_handler_model.favorite_item_exception import FavoriteItemException
from model.requst_response_models.customer_favorite_item_request import CustomerFavoriteItemRequest
from model.requst_response_models.customer_favorite_item_response import CustomerFavoriteItemResponse
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


@router.post("/create", status_code=201)
async def create_favorite_item(customer_request: CustomerFavoriteItemRequest) -> int:
    result: Union[int, CustomerException, FavoriteItemException] = await customer_favorite_item_service.create_favorite_item(customer_request)

    final_result = _exception_handler(result)

    return final_result


@router.put("/update-{favorite_item_id}", status_code=200)
async def update_favorite_item_by_id(favorite_item_id: int, favorite_item: CustomerFavoriteItem) -> str:
    result: Union[str, FavoriteItemException, CustomerException] = await customer_favorite_item_service.update_favorite_item_by_id(favorite_item_id, favorite_item)

    final_result = _exception_handler(result)

    return final_result


@router.get("/get-item-{favorite_item_id}", response_model=CustomerFavoriteItemResponse, status_code=200)
async def get_favorite_item_by_id(favorite_item_id: int) -> CustomerFavoriteItemResponse:
    result: Union[CustomerFavoriteItemResponse, FavoriteItemException] = await customer_favorite_item_service.get_favorite_item_by_id(favorite_item_id)

    final_result = _exception_handler(result)

    return final_result


@router.get("/get-customer-{customer_id}")
async def get_favorite_items_by_customer_id(customer_id: int) -> List[CustomerFavoriteItemResponse]:
    result: Union[List[CustomerFavoriteItemResponse], CustomerException] = await customer_favorite_item_service.get_favorite_items_by_customer_id(customer_id)

    final_result = _exception_handler(result)

    return final_result


@router.delete("/delete-{favorite_item_id}", status_code=200)
async def delete_favorite_item_by_id(favorite_item_id: int) -> str:
    result: Union[str, FavoriteItemException] = await customer_favorite_item_service.delete_favorite_item_by_id(favorite_item_id)

    final_result = _exception_handler(result)

    return final_result