import httpx
from typing import List, Optional

from fastapi import HTTPException

from api.internal_api.seller_service.model.item_response import ItemResponse
from database import config


async def _get_from_seller_service(url: str, params: Optional[dict] = None) -> dict:

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params)

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


async def _try_get_from_seller_service(url: str, params: Optional[dict] = None) -> Optional[dict]:

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params)

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
        return None

    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail="Seller Service returned an error"
        )

    return response.json()


async def get_lowest_price_item_by_name(item_name: str, seller_name: Optional[str] = None) -> ItemResponse:
    url = f"{config.SELLER_SERVICE_BASE_URL}/item/by-name"
    params = {"item_name": item_name}
    if seller_name:
        params["seller_name"] = seller_name

    data = await _get_from_seller_service(url, params=params)
    return ItemResponse(**data)




async def find_lowest_price_item_by_name(item_name: str, seller_name: Optional[str] = None) -> Optional[ItemResponse]:
    url = f"{config.SELLER_SERVICE_BASE_URL}/item/by-name"

    params = {"item_name": item_name}
    if seller_name:
        params["seller_name"] = seller_name
    data = await _try_get_from_seller_service(url, params=params)

    if data is None:
        return None

    return ItemResponse(**data)


async def get_item_by_item_id(item_id: int) -> ItemResponse:
    url = f"{config.SELLER_SERVICE_BASE_URL}/item/{item_id}"

    data = await _get_from_seller_service(url)

    return ItemResponse(**data)