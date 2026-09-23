
from typing import Optional, List

from fastapi import APIRouter, HTTPException

from model.customer import Customer
from service import customer_service

router: APIRouter = APIRouter(
    prefix="/customer",
    tags=["customer"]
)


@router.post("/create_customer", status_code=201)
async def create_customer(customer: Customer) -> str:

    result: Optional[int] = await customer_service.create_customer(customer)
    if result is None:
        raise HTTPException(status_code=409, detail="Cannot creat VIP customer - out of 10 customers limit")

    return "customer created successfully"


@router.put("/update_customer-{customer_id}",status_code=200)
async def update_customer_by_id(customer_id: int, customer: Customer) -> str:

    result: Optional[str] = await customer_service.update_customer_by_id(customer_id, customer)
    if not result:
        raise HTTPException(status_code=404, detail=f"Customer with id: {customer_id} not found")

    if result == "MAXED":
        raise HTTPException(status_code=409, detail="Cannot creat VIP customer - out of 10 customers limit")

    return result


@router.get("/get_customer-{customer_id}", response_model=Customer, status_code=200)
async def get_customer_by_id(customer_id: int) -> Optional[Customer]:

    result: Optional[Customer] = await customer_service.get_customer_by_id(customer_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Customer with id: {customer_id} not found")

    else:
        return result


@router.get("/get_all_customers",response_model=List[Customer], status_code=200)
async def get_all_customers() -> List[Customer]:

    return await customer_service.get_all_customers()


@router.delete("/delete_customer-{customer_id}", status_code=200)
async def delete_customer_by_id(customer_id: int) -> str:

    result: Optional[str] = await customer_service.delete_customer_by_id(customer_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Customer with id: {customer_id} not found")

    return result