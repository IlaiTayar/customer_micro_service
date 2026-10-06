from typing import List, Optional

from databases.interfaces import Record
from database import database
from model.base_models.customer_favorite_item import CustomerFavoriteItem


TABLE_NAME = "customer_favorite_item"


def _to_customer_favorite_item(record: Record) -> CustomerFavoriteItem:
    return CustomerFavoriteItem(
        favorite_item_id=record["favorite_item_id"],
        customer_id=record["customer_id"],
        item_id=record["item_id"]
    )


async def create_favorite_item(favorite_item: CustomerFavoriteItem) -> int:
    query = f"""
        INSERT INTO {TABLE_NAME} (customer_id, item_id)
        VALUES (:customer_id, :item_id)
    """

    values = {"customer_id": favorite_item.customer_id, "item_id": favorite_item.item_id}

    return await database.execute(query, values)


async def update_favorite_item_by_id(favorite_item_id: int, favorite_item: CustomerFavoriteItem) -> str:
    query = f"""
        UPDATE {TABLE_NAME}
        SET customer_id = :customer_id,
            item_id = :item_id
        WHERE favorite_item_id = :favorite_item_id
    """

    values = {
        "favorite_item_id": favorite_item_id,
        "customer_id": favorite_item.customer_id,
        "item_id": favorite_item.item_id,
    }

    await database.execute(query, values)
    return f"favorite item with id: {favorite_item_id} was updated successfully for customer with id: {favorite_item.customer_id}"


async def get_favorite_item_by_id(favorite_item_id: int) -> Optional[CustomerFavoriteItem]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE favorite_item_id=:favorite_item_id"

    record: Optional[Record] = await database.fetch_one(query, values={"favorite_item_id": favorite_item_id})

    return _to_customer_favorite_item(record) if record else None



async def get_favorite_items_by_customer_id(customer_id: int) -> List[CustomerFavoriteItem]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE customer_id=:customer_id"

    records: List[Record] = await database.fetch_all(query, values={"customer_id": customer_id})
    return [_to_customer_favorite_item(record) for record in records]


async def get_by_item_id(item_id: int) -> Optional[CustomerFavoriteItem]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE item_id=:item_id"

    record: Optional[Record] = await database.fetch_one(query, values={"item_id": item_id})
    return _to_customer_favorite_item(record) if record else None



async def delete_favorite_item_by_id(favorite_item_id: int) -> str:
    query = f"DELETE FROM {TABLE_NAME} WHERE favorite_item_id=:favorite_item_id"

    await database.execute(query, values={"favorite_item_id": favorite_item_id})
    return f"favorite item with id: {favorite_item_id} was deleted successfully"


async def count_favorites_by_item_id(item_id: int) -> int:
    query = f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE item_id=:item_id"

    result = await database.fetch_val(query, values={"item_id": item_id})
    return int(result or 0)