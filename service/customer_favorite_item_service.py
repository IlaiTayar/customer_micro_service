from typing import Optional, List, Union

from api.internal_api.seller_service.model.item_response import ItemResponse
from api.internal_api.seller_service import seller_service_api
from model.base_models.customer import Customer
from model.base_models.customer_favorite_item import CustomerFavoriteItem
from model.exception_handler_model.customer_exception import CustomerException
from model.exception_handler_model.favorite_item_exception import FavoriteItemException
from model.requst_response_models.customer_favorite_item_request import CustomerFavoriteItemRequest
from model.requst_response_models.customer_favorite_item_response import CustomerFavoriteItemResponse
from model.requst_response_models.customer_favorites_response import CustomerFavoritesResponse, FavoriteItemEntry
from model.requst_response_models.favorite_item_update_request import FavoriteItemUpdateRequest
from repository import customer_favorite_item_repository
from service import customer_service


async def get_favorite_item_by_customer_id_and_item_id(
    customer_id: int,
    item_id: int
) -> Optional[CustomerFavoriteItem]:
    return await customer_favorite_item_repository.get_by_customer_id_and_item_id(
        customer_id,
        item_id
    )


async def create_favorite_item(
    customer_request: CustomerFavoriteItemRequest
) -> Union[CustomerFavoriteItemResponse, CustomerException, FavoriteItemException]:
    customer = await customer_service.get_customer_by_id(customer_request.customer_id)
    if isinstance(customer, CustomerException):
        return customer

    item = await seller_service_api.find_lowest_price_item_by_name(customer_request.item_name)
    if item is None or item.item_id is None:
        return FavoriteItemException.ITEM_NOT_FOUND

    existing_favorite = await get_favorite_item_by_customer_id_and_item_id(
        customer.customer_id,
        item.item_id
    )
    if existing_favorite is not None:
        return FavoriteItemException.FAVORITE_ITEM_ALREADY_EXISTS

    favorite_item = CustomerFavoriteItem(
        customer_id=customer.customer_id,
        item_id=item.item_id
    )
    favorite_item_id = await customer_favorite_item_repository.create_favorite_item(favorite_item)

    return CustomerFavoriteItemResponse(
        favorite_item_id=favorite_item_id,
        customer=customer,
        item_response=item
    )


async def update_favorite_item_by_id(
    favorite_item_id: int,
    favorite_item_request: FavoriteItemUpdateRequest
) -> Union[CustomerFavoriteItemResponse, FavoriteItemException, CustomerException]:
    existing_favorite = await get_favorite_item_by_id(favorite_item_id)
    if isinstance(existing_favorite, (FavoriteItemException, CustomerException)):
        return existing_favorite

    item = await seller_service_api.find_lowest_price_item_by_name(
        favorite_item_request.item_name
    )
    if item is None or item.item_id is None:
        return FavoriteItemException.SOMTHING_WENT_WRONG

    existing_pair = await get_favorite_item_by_customer_id_and_item_id(
        existing_favorite.customer.customer_id,
        item.item_id
    )

    if existing_pair is not None and existing_pair.favorite_item_id != favorite_item_id:
        return FavoriteItemException.FAVORITE_ITEM_ALREADY_EXISTS

    updated_favorite = CustomerFavoriteItem(
        favorite_item_id=favorite_item_id,
        customer_id=existing_favorite.customer.customer_id,
        item_id=item.item_id
    )

    await customer_favorite_item_repository.update_favorite_item_by_id(
        favorite_item_id,
        updated_favorite
    )

    return CustomerFavoriteItemResponse(
        favorite_item_id=favorite_item_id,
        customer=existing_favorite.customer,
        item_response=item
    )


async def get_favorite_item_by_id(
    favorite_item_id: int
) -> Union[CustomerFavoriteItemResponse, FavoriteItemException, CustomerException]:
    favorite_item = await customer_favorite_item_repository.get_favorite_item_by_id(
        favorite_item_id
    )
    if favorite_item is None:
        return FavoriteItemException.FAVORITE_ITEM_NOT_FOUND

    customer = await customer_service.get_customer_by_id(favorite_item.customer_id)
    if isinstance(customer, CustomerException):
        return customer

    item = await seller_service_api.get_item_by_item_id(favorite_item.item_id)

    return CustomerFavoriteItemResponse(
        favorite_item_id=favorite_item_id,
        customer=customer,
        item_response=item
    )


async def get_favorite_items_by_customer_id(
    customer_id: int
) -> Union[CustomerFavoritesResponse, CustomerException]:
    customer = await customer_service.get_customer_by_id(customer_id)
    if isinstance(customer, CustomerException):
        return customer

    customer_favorite_items = await customer_favorite_item_repository.get_favorite_items_by_customer_id(
        customer_id
    )

    favorite_items = [
        FavoriteItemEntry(
            favorite_item_id=favorite_item.favorite_item_id,
            item_response=await seller_service_api.get_item_by_item_id(favorite_item.item_id)
        )
        for favorite_item in customer_favorite_items
    ]

    return CustomerFavoritesResponse(
        customer=customer,
        favorite_items=favorite_items
    )


async def delete_favorite_item_by_id(
    favorite_item_id: int
) -> Union[str, FavoriteItemException]:
    existing_favorite = await get_favorite_item_by_id(favorite_item_id)
    if isinstance(existing_favorite, FavoriteItemException):
        return existing_favorite

    return await customer_favorite_item_repository.delete_favorite_item_by_id(
        favorite_item_id
    )


async def count_favorites_by_item_id(item_id: int) -> int:
    return await customer_favorite_item_repository.count_favorites_by_item_id(item_id)


async def lookup_item_by_name(
    customer_request: CustomerFavoriteItemRequest
) -> Union[CustomerFavoriteItemResponse, CustomerException, FavoriteItemException]:
    customer = await customer_service.get_customer_by_id(customer_request.customer_id)
    if isinstance(customer, CustomerException):
        return customer

    item = await seller_service_api.find_lowest_price_item_by_name(customer_request.item_name)
    if item is None or item.item_id is None:
        return FavoriteItemException.ITEM_NOT_FOUND

    existing_favorite = await get_favorite_item_by_customer_id_and_item_id(
        customer.customer_id,
        item.item_id
    )

    if existing_favorite is None:
        return FavoriteItemException.ITEM_NOT_IN_FAVORITES

    return CustomerFavoriteItemResponse(
        favorite_item_id=existing_favorite.favorite_item_id,
        customer=customer,
        item_response=item
    )


async def lookup_favorite_item_by_id(
    customer_id: int,
    favorite_item_id: int
) -> Union[CustomerFavoriteItemResponse, CustomerException, FavoriteItemException]:
    favorite = await get_favorite_item_by_id(favorite_item_id)

    if isinstance(favorite, FavoriteItemException):
        if favorite == FavoriteItemException.FAVORITE_ITEM_NOT_FOUND:
            return FavoriteItemException.ITEM_NOT_IN_FAVORITES
        return favorite

    if isinstance(favorite, CustomerException):
        return favorite

    if favorite.customer.customer_id != customer_id:
        return FavoriteItemException.ITEM_NOT_IN_FAVORITES

    return favorite
