from typing import Dict, Optional, List, Union

from databases.interfaces import Record

from database import database
from model.base_models.order import Order


TABLE_NAME = "orders"


def _to_order(record: Record) -> Order:
    return Order(
        order_id=record["order_id"],
        customer_id=record["customer_id"],
        item_name=record["item_name"],
        price=record["price"]
    )


async def create_order(order: Order):
    query = f"""
    INSERT INTO {TABLE_NAME} ( customer_id, item_name, price)
    VALUES (:customer_id, :item_name, :price)
    """

    values: Dict[str, Union[str, float, None]] = {
        "customer_id": order.customer_id,
        "item_name": order.item_name,
        "price": order.price
    }

    await database.execute(query, values)



async def update_order_by_id(order_id: int, order: Order) -> str:
    query = f"""
    update {TABLE_NAME} 
    set item_name = :item_name, 
    price = :price 
    where order_id = :order_id
    """

    values: Dict[str, Union[str, float]] = {
        "item_name": order.item_name,
        "price": order.price,
        "order_id": order_id
    }

    await database.execute(query, values)
    return f"order with id: {order_id} updated successfully"


async def get_order_by_id(order_id: Optional[int]) -> Optional[Order]:
    query = f"""
    select * from {TABLE_NAME} where order_id = :order_id
    """

    values: Dict[str, Optional[int]] = {
        "order_id": order_id
    }

    record: Optional[Record] = await database.fetch_one(query, values)
    return _to_order(record) if record else None


async def get_orders_by_customer_id(customer_id: Optional[int]) -> List[Order]:
    query = f"""
    select * from {TABLE_NAME} where customer_id = :customer_id
    """

    values: Dict[str, Optional[int]] = {
        "customer_id": customer_id
    }

    records: List[Record] = await database.fetch_all(query, values)
    return [_to_order(record) for record in records]


async def get_all_orders() -> List[Order]:
    query = f"""
    select * from {TABLE_NAME}
    """

    records: List[Record] = await database.fetch_all(query)
    return [_to_order(record) for record in records]


async def delete_order_by_id(order_id: Optional[int]) -> str:
    query = f"""
    delete from {TABLE_NAME} where order_id = :order_id
    """

    values: Dict[str, Optional[int]] = {
        "order_id": order_id
    }

    await database.execute(query, values)
    return "order deleted successfully"