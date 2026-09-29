from typing import Optional, List

from api.internal_api.seller_service.model.item_response import ItemResponse
from api.internal_api.seller_service import seller_service_api
from model.base_models.customer import Customer
from model.base_models.customer_favorite_item import CustomerFavoriteItem
from model.requst_response_models.customer_favorite_item_request import CustomerFavoriteItemRequest
from model.requst_response_models.customer_favorite_item_response import CustomerFavoriteItemResponse
from repository import customer_favorite_item_repository
from service import customer_service


async def create_favorite_item(customer_request: CustomerFavoriteItemRequest) -> Optional[int]:
        customer = await customer_service.get_customer_by_id(customer_request.customer_id)
        if customer is None:
            return None

        item = await seller_service_api.get_lowest_price_item_by_name(customer_request.item_name)
        if item is None:
            return None

        existing_favorite = await customer_favorite_item_repository.get_by_customer_id_and_item_id(customer_id=customer.customer_id, item_id=item.item_id)

        if existing_favorite is not None:
            return None

        favorite_item = CustomerFavoriteItem(customer_id=customer.customer_id, item_id=item.item_id)

        return await customer_favorite_item_repository.create_favorite_item(favorite_item)


async def update_favorite_item_by_id(favorite_item_id: int, favorite_item: CustomerFavoriteItem) -> Optional[str]:
    existing_favorite_item: Optional[CustomerFavoriteItemResponse] = await get_favorite_item_by_id(favorite_item_id)
    if existing_favorite_item is None:
        return None
    existing_item_id: Optional[CustomerFavoriteItem] = await customer_favorite_item_repository.get_by_customer_id_and_item_id(existing_favorite_item.customer_id,
                                                                                                                              favorite_item.item_id)
    if existing_item_id is not None:
        return None

    item_in_sellers = await seller_service_api.get_item_by_item_id(favorite_item.item_id)
    if item_in_sellers is None:
        return None

    await customer_favorite_item_repository.update_favorite_item_by_id(favorite_item_id, favorite_item)

    return f"favorite item with id: {favorite_item_id} updated successfully"


async def get_favorite_item_by_id(favorite_item_id: int) -> Optional[CustomerFavoriteItemResponse]:
    favorite_item: Optional[CustomerFavoriteItem] = await customer_favorite_item_repository.get_favorite_item_by_id(favorite_item_id)
    if favorite_item is None:
        return None

    item = await seller_service_api.get_item_by_item_id(favorite_item.item_id)
    favorite_item_response: CustomerFavoriteItemResponse = CustomerFavoriteItemResponse(favorite_item_id=favorite_item_id, customer_id=favorite_item.customer_id, item_response=item)

    return favorite_item_response


async def get_favorite_items_by_customer_id(customer_id: int) -> Optional[List[CustomerFavoriteItemResponse]]:
    existing_customer: Optional[Customer] = await customer_service.get_customer_by_id(customer_id)
    if existing_customer is None:
        return None

    customer_favorite_items: List[CustomerFavoriteItem] = await customer_favorite_item_repository.get_favorite_items_by_customer_id(customer_id)
    response_list:List[CustomerFavoriteItemResponse] = [
        CustomerFavoriteItemResponse(favorite_item_id= favorite_item.favorite_item_id,
        customer_id=favorite_item.customer_id,
        item_response= await seller_service_api.get_item_by_item_id(favorite_item.item_id))
        for favorite_item in customer_favorite_items
    ]
    return response_list

async def get_by_customer_id_and_item_id(customer_id: int, item_id: int) -> Optional[CustomerFavoriteItemResponse]:
    existing_customer: Optional[Customer] = await customer_service.get_customer_by_id(customer_id)
    if existing_customer is None:
        return None

    existing_favorite_item: Optional[CustomerFavoriteItem] = await customer_favorite_item_repository.get_by_customer_id_and_item_id(customer_id, item_id)
    if existing_favorite_item is None:
        return None

    item_response: ItemResponse = await seller_service_api.get_item_by_item_id(item_id)
    favorite_item_response: CustomerFavoriteItemResponse = CustomerFavoriteItemResponse(favorite_item_id=existing_favorite_item.favorite_item_id,
                                                                                        customer_id=customer_id, item_response=item_response)
    return favorite_item_response


async def delete_favorite_item_by_id(favorite_item_id: int) -> Optional[str]:
    existing_favorite_item = await get_favorite_item_by_id(favorite_item_id)
    if existing_favorite_item is None:
        return None

    deleted = await customer_favorite_item_repository.delete_favorite_item_by_id(favorite_item_id)
    return deleted