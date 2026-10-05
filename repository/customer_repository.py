import json
from typing import Dict, Optional, List, Union

from databases.interfaces import Record

from database import database
from model.base_models.customer import Customer, CustomerStatus
from repository import cache_repository

TABLE_NAME = "customer"


def _to_customer(record: Record) -> Customer:
    return Customer(
        customer_id=record["customer_id"],
        first_name=record["first_name"],
        last_name=record["last_name"],
        email=record["email"],
        status=record["status"],
    )


async def create_customer(customer: Customer) -> int:
    query: str = f"""
    INSERT INTO {TABLE_NAME} (first_name, last_name, email, status)
    VALUES (:first_name, :last_name, :email, :status)
    """

    values: Dict[str, str] = {
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email,
        "status": customer.status.name
    }

    customer_id = await database.execute(query, values)
    return customer_id


async def update_customer_by_id(customer_id: int, customer: Customer) -> str:
    if cache_repository.is_key_exists(str(customer_id)):
        cache_repository.remove_cache_entity(str(customer_id))

    query: str = f""" 
    UPDATE {TABLE_NAME}
    SET first_name = :first_name, 
    last_name = :last_name, 
    email = :email,
    status = :status
    WHERE customer_id = :customer_id
    """

    values: Dict[str, Union[str, int]] = {
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email,
        "customer_id": customer_id,
        "status": customer.status.name
    }

    await database.execute(query, values)
    return f"customer with id: {customer_id} updated successfully"
    
    
async def get_customer_by_id(customer_id: Optional[int]) -> Optional[Customer]:
    if cache_repository.is_key_exists(str(customer_id)):
        str_customer = cache_repository.get_cache_entity(str(customer_id))

        if str_customer:
            customer = _to_customer(json.loads(str_customer))
            # Refresh the TTL on a cache hit.
            cache_repository.remove_cache_entity(str(customer_id))
            cache_repository.create_cache_entity(str(customer_id), customer.model_dump_json())
            return customer

        return None

    query: str = f"""
    SELECT * FROM {TABLE_NAME} WHERE customer_id = :customer_id
    """

    values: Dict[str, Optional[int]] = {
        "customer_id": customer_id,
    }

    record: Optional[Record] = await database.fetch_one(query, values)
    if record:
        customer = _to_customer(record)
        cache_repository.create_cache_entity(str(customer_id), customer.model_dump_json())
        return customer

    return None


async def get_customer_by_status(status: CustomerStatus) -> List[Customer]:
    query: str = f"""
    SELECT * FROM {TABLE_NAME} WHERE status = :status
    """
    values: Dict[str, str] = {
    "status": status.name
    }

    records:List[Record] = await database.fetch_all(query, values)
    return [_to_customer(record) for record in records]


async def get_customer_by_email(email: str) -> Optional[Customer]:
    query: str = f"""
    select * from {TABLE_NAME} where email = :email
    """

    record: Optional[Record] = await database.fetch_one(query, values={"email": email})
    return _to_customer(record) if record else None


async def get_all_customers() -> List[Customer]:
    query: str = f"""
    SELECT * FROM {TABLE_NAME}
    """

    records: List[Record] = await database.fetch_all(query)
    return [_to_customer(record) for record in records]


async def delete_customer_by_id(customer_id: int) -> str:
    if cache_repository.is_key_exists(str(customer_id)):
        cache_repository.remove_cache_entity(str(customer_id))

    query: str = f"""
    DELETE FROM {TABLE_NAME} WHERE customer_id = :customer_id
    """

    values: Dict[str, int] = {
        "customer_id": customer_id,
    }

    await database.execute(query, values)
    return "customer deleted successfully"