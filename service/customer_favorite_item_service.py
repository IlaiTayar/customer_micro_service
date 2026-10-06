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
from repository import customer_favorite_item_repository
from service import customer_service


async def create_favorite_item(customer_request: CustomerFavoriteItemRequest) -> Union[int, CustomerException, FavoriteItemException]:
        customer: Union[Customer, CustomerException] = await customer_service.get_customer_by_id(customer_request.customer_id)
        if isinstance(customer, CustomerException):
            return customer

        item: ItemResponse = await seller_service_api.get_lowest_price_item_by_name(customer_request.item_name)

        if customer.customer_id is not None and item.item_id is not None:
            existing_favorite: Union[CustomerFavoriteItemResponse, FavoriteItemException, CustomerException] = await get_by_customer_id_and_item_id(customer_id=customer.customer_id, item_id=item.item_id)

            if isinstance(existing_favorite, CustomerException):
                return existing_favorite

            if isinstance(existing_favorite, CustomerFavoriteItemResponse):
                return FavoriteItemException.FAVORITE_ITEM_ALREADY_EXISTS

            favorite_item = CustomerFavoriteItem(customer_id=customer.customer_id, item_id=item.item_id)

            return await customer_favorite_item_repository.create_favorite_item(favorite_item)

        return FavoriteItemException.SOMTHING_WENT_WRONG


async def update_favorite_item_by_id(favorite_item_id: int, favorite_item: CustomerFavoriteItem) -> Union[str, FavoriteItemException, CustomerException]:
    existing_favorite_item: Union[CustomerFavoriteItemResponse, FavoriteItemException] = await get_favorite_item_by_id(favorite_item_id)
    if isinstance(existing_favorite_item, FavoriteItemException):
        return existing_favorite_item

    existing_item_id: Union[CustomerFavoriteItemResponse, FavoriteItemException, CustomerException] = await get_by_customer_id_and_item_id(existing_favorite_item.customer_id, favorite_item.item_id)
    if isinstance(existing_item_id, FavoriteItemException) or isinstance(existing_item_id, CustomerException):
        return existing_item_id

    item_in_sellers = await seller_service_api.get_item_by_item_id(favorite_item.item_id)
    if item_in_sellers is not None:
        await customer_favorite_item_repository.update_favorite_item_by_id(favorite_item_id, favorite_item)

        return f"favorite item with id: {favorite_item_id} updated successfully"

    return FavoriteItemException.SOMTHING_WENT_WRONG


async def get_favorite_item_by_id(favorite_item_id: int) -> Union[CustomerFavoriteItemResponse, FavoriteItemException]:
    favorite_item: Optional[CustomerFavoriteItem] = await customer_favorite_item_repository.get_favorite_item_by_id(favorite_item_id)
    if favorite_item is None:
        return FavoriteItemException.FAVORITE_ITEM_NOT_FOUND

    item = await seller_service_api.get_item_by_item_id(favorite_item.item_id)
    favorite_item_response: CustomerFavoriteItemResponse = CustomerFavoriteItemResponse(favorite_item_id=favorite_item_id, customer_id=favorite_item.customer_id, item_response=item)

    return favorite_item_response


async def get_favorite_items_by_customer_id(customer_id: int) -> Union[CustomerFavoritesResponse, CustomerException]:
    existing_customer: Union[Customer, CustomerException] = await customer_service.get_customer_by_id(customer_id)
    if isinstance(existing_customer, CustomerException):
        return existing_customer

    customer_favorite_items: List[CustomerFavoriteItem] = await customer_favorite_item_repository.get_favorite_items_by_customer_id(customer_id)
    favorite_items: List[FavoriteItemEntry] = [
        FavoriteItemEntry(
            favorite_item_id=favorite_item.favorite_item_id,
            item_response=await seller_service_api.get_item_by_item_id(favorite_item.item_id),
        )
        for favorite_item in customer_favorite_items
    ]
    return CustomerFavoritesResponse(customer=existing_customer, favorite_items=favorite_items)

async def get_by_customer_id_and_item_id(customer_id: int, item_id: int) -> Union[CustomerFavoriteItemResponse, FavoriteItemException, CustomerException]:
    existing_customer: Union[Customer, CustomerException] = await customer_service.get_customer_by_id(customer_id)
    if isinstance(existing_customer, CustomerException):
        return existing_customer

    existing_favorite_item: Optional[CustomerFavoriteItem] = await customer_favorite_item_repository.get_by_customer_id_and_item_id(customer_id, item_id)
    if existing_favorite_item is None:
        return FavoriteItemException.FAVORITE_ITEM_NOT_FOUND

    item_response: ItemResponse = await seller_service_api.get_item_by_item_id(item_id)

    favorite_item_response: CustomerFavoriteItemResponse = CustomerFavoriteItemResponse(favorite_item_id=existing_favorite_item.favorite_item_id,
                                                                                        customer_id=customer_id, item_response=item_response)

    return favorite_item_response


async def delete_favorite_item_by_id(favorite_item_id: int) -> Union[str, FavoriteItemException]:
    existing_favorite_item: Union[CustomerFavoriteItemResponse, FavoriteItemException] = await get_favorite_item_by_id(favorite_item_id)
    if isinstance(existing_favorite_item, FavoriteItemException):
        return existing_favorite_item

    deleted = await customer_favorite_item_repository.delete_favorite_item_by_id(favorite_item_id)
    return deleted


async def count_favorites_by_item_id(item_id: int) -> int:
    return await customer_favorite_item_repository.count_favorites_by_item_id(item_id)


async def _add_to_favorites_if_missing(customer_id: int, item: ItemResponse) -> Union[CustomerFavoriteItemResponse, FavoriteItemException]:
    if item.item_id is None:
        return FavoriteItemException.SOMTHING_WENT_WRONG

    existing_favorite_item: Optional[CustomerFavoriteItem] = await customer_favorite_item_repository.get_by_customer_id_and_item_id(customer_id, item.item_id)

    if existing_favorite_item is None:
        favorite_item = CustomerFavoriteItem(customer_id=customer_id, item_id=item.item_id)
        new_favorite_item_id = await customer_favorite_item_repository.create_favorite_item(favorite_item)
        return CustomerFavoriteItemResponse(favorite_item_id=new_favorite_item_id, customer_id=customer_id, item_response=item)

    return CustomerFavoriteItemResponse(favorite_item_id=existing_favorite_item.favorite_item_id, customer_id=customer_id, item_response=item)


async def lookup_item_by_name_and_favorite(customer_id: int, item_name: str) -> Union[CustomerFavoriteItemResponse, CustomerException, FavoriteItemException]:
    customer: Union[Customer, CustomerException] = await customer_service.get_customer_by_id(customer_id)
    if isinstance(customer, CustomerException):
        return customer

    item: ItemResponse = await seller_service_api.get_lowest_price_item_by_name(item_name)

    return await _add_to_favorites_if_missing(customer.customer_id, item)


async def lookup_item_by_id_and_favorite(customer_id: int, item_id: int) -> Union[CustomerFavoriteItemResponse, CustomerException, FavoriteItemException]:
    customer: Union[Customer, CustomerException] = await customer_service.get_customer_by_id(customer_id)
    if isinstance(customer, CustomerException):
        return customer

    item: ItemResponse = await seller_service_api.get_item_by_item_id(item_id)

    return await _add_to_favorites_if_missing(customer.customer_id, item)