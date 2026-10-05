import httpx
from fastapi import HTTPException

from api.internal_api.seller_service.model.item_response import ItemResponse
from database import config


async def _get_from_seller_service(url: str) -> dict:

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)

    except (httpx.ConnectError, httpx.TimeoutException) as err:
        raise HTTPException(
            status_code=503,
            detail=f"Seller Service unavailable: {err}"
        )

    except httpx.HTTPError as err:
        raise HTTPException(
            status_code=502,
            detail=f"Error communicating with Seller Service: {err}"
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail=response.json().get("detail", "Item not found")
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail="Seller Service returned an error"
        )

    return response.json()


async def get_lowest_price_item_by_name(item_name: str) -> ItemResponse:
    url = f"{config.SELLER_SERVICE_BASE_URL}/item/get-name-{item_name}"

    data = await _get_from_seller_service(url)

    return ItemResponse(**data)


async def get_item_by_item_id(item_id: int) -> ItemResponse:
    url = f"{config.SELLER_SERVICE_BASE_URL}/item/get-id-{item_id}"

    data = await _get_from_seller_service(url)

    return ItemResponse(**data)