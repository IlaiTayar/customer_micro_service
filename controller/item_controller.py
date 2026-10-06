from typing import List, Optional

from fastapi import APIRouter, Query

from api.internal_api.seller_service import seller_service_api
from api.internal_api.seller_service.model.item_response import ItemResponse

router = APIRouter(prefix="/item", tags=["item"])


@router.get("/by-name", response_model=ItemResponse, status_code=200)
async def get_item_by_name(
    item_name: str = Query(...),
    seller_name: Optional[str] = Query(None)
) -> ItemResponse:
    return await seller_service_api.get_lowest_price_item_by_name(item_name, seller_name)


@router.get("/by-seller-name", response_model=List[ItemResponse], status_code=200)
async def get_items_by_seller_name(seller_name: str = Query(...)) -> List[ItemResponse]:
    return await seller_service_api.get_items_by_seller_name(seller_name)


@router.get("/{item_id}", response_model=ItemResponse, status_code=200)
async def get_item_by_id(item_id: int) -> ItemResponse:
    return await seller_service_api.get_item_by_item_id(item_id)
