from typing import Optional, List, Union

from api.internal_api.seller_service.model.item_response import ItemResponse
from api.internal_api.seller_service import seller_service_api
from model.base_models.customer import Customer
from model.base_models.customer_favorite_item import CustomerFavoriteItem
from model.exception_handler_model.customer_exception import CustomerException
from model.exception_handler_model.favorite_item_exception import FavoriteItemException
from model.requst_response_models.customer_favorite_item_request import CustomerFavoriteItemRequest
from model.requst_response_models.customer_favorite_item_response import CustomerFavoriteItemResponse
from repository import customer_favorite_item_repository
from service import customer_service


async def create_favorite_item(customer_request: CustomerFavoriteItemRequest) -> Union[int, CustomerException, FavoriteItemException]:
        customer: Union[Customer, CustomerException] = await customer_service.get_customer_by_id(customer_request.customer_id)
        if isinstance(customer, CustomerException):
            return customer

        item: ItemResponse = await seller_service_api.get_lowest_price_item_by_name(customer_request.item_name)

        if customer.customer_id is not None and item.item_id is not None:
            existing_favorite: Union[CustomerFavoriteItemResponse, FavoriteItemException, CustomerException] = await get_by_customer_id_and_item_id(customer_id=customer.customer_id, item_id=item.item_id)

            if isinstance(existing_favorite, FavoriteItemException) or isinstance(existing_favorite, CustomerException):
                return existing_favorite

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


async def get_favorite_items_by_customer_id(customer_id: int) -> Union[List[CustomerFavoriteItemResponse], CustomerException]:
    existing_customer: Union[Customer, CustomerException] = await customer_service.get_customer_by_id(customer_id)
    if isinstance(existing_customer, CustomerException):
        return existing_customer

    customer_favorite_items: List[CustomerFavoriteItem] = await customer_favorite_item_repository.get_favorite_items_by_customer_id(customer_id)
    response_list:List[CustomerFavoriteItemResponse] = [
        CustomerFavoriteItemResponse(favorite_item_id= favorite_item.favorite_item_id,
        customer_id=favorite_item.customer_id,
        item_response= await seller_service_api.get_item_by_item_id(favorite_item.item_id))
        for favorite_item in customer_favorite_items
    ]
    return response_list

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