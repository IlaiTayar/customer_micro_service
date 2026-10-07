from typing import Optional, List

from databases.interfaces import Record

from database import database
from model.base_models.order import Order

TABLE_NAME = "orders"


def _to_order(record: Record) -> Order:
    return Order(
        order_id=record["order_id"],
        customer_id=record["customer_id"],
        item_id=record["item_id"],
        item_name=record["item_name"],
        price=record["price"],
    )


async def create_order(order: Order) -> None:
    query = f"""
        INSERT INTO {TABLE_NAME} (customer_id, item_id, item_name, price)
        VALUES (:customer_id, :item_id, :item_name, :price)
    """
    await database.execute(
        query,
        {
            "customer_id": order.customer_id,
            "item_id": order.item_id,
            "item_name": order.item_name,
            "price": order.price,
        },
    )


async def update_order_by_id(order_id: int, order: Order) -> str:
    query = f"""
        UPDATE {TABLE_NAME}
        SET item_id=:item_id,
            item_name=:item_name,
            price=:price
        WHERE order_id=:order_id
    """
    await database.execute(
        query,
        {
            "item_id": order.item_id,
            "item_name": order.item_name,
            "price": order.price,
            "order_id": order_id,
        },
    )
    return f"order with id: {order_id} updated successfully"


async def get_order_by_id(order_id: int) -> Optional[Order]:
    record = await database.fetch_one(
        f"SELECT * FROM {TABLE_NAME} WHERE order_id=:order_id",
        {"order_id": order_id},
    )
    return _to_order(record) if record else None


async def get_orders_by_customer_id(customer_id: int) -> List[Order]:
    records = await database.fetch_all(
        f"SELECT * FROM {TABLE_NAME} WHERE customer_id=:customer_id",
        {"customer_id": customer_id},
    )
    return [_to_order(record) for record in records]


async def get_all_orders() -> List[Order]:
    records = await database.fetch_all(f"SELECT * FROM {TABLE_NAME}")
    return [_to_order(record) for record in records]


async def delete_order_by_id(order_id: int) -> str:
    await database.execute(
        f"DELETE FROM {TABLE_NAME} WHERE order_id=:order_id",
        {"order_id": order_id},
    )
    return "order deleted successfully"


async def count_orders_by_item_id(item_id: int) -> int:
    result = await database.fetch_val(
        f"SELECT count(*) FROM {TABLE_NAME} WHERE item_id=:item_id",
    )
    return int(result or 0)
