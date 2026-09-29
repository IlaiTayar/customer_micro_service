import httpx
from api.internal_api.seller_service.model.item_response import ItemResponse
from database import config


async def get_lowest_price_item_by_name(item_name: str) -> ItemResponse:
    url = f"{config.SELLER_SERVICE_BASE_URL}/item/get-name-{item_name}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

        return ItemResponse(**data)


async def get_item_by_item_id(item_id: int) -> ItemResponse:
    url = f"{config.SELLER_SERVICE_BASE_URL}/item/get-id-{item_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

        return ItemResponse(**data)