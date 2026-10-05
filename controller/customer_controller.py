
from typing import List, Union, Any

from fastapi import APIRouter, HTTPException

from model.base_models.customer import Customer
from model.exception_handler_model.customer_exception import CustomerException
from service import customer_service

router: APIRouter = APIRouter(
    prefix="/customer",
    tags=["customer"]
)


def _exception_handler(result: Any) -> Any:
    if isinstance(result, CustomerException):

        if result == CustomerException.CUSTOMER_EXISTS:
            raise HTTPException(status_code=409, detail=f"{CustomerException.CUSTOMER_EXISTS} with this email")

        if result == CustomerException.VIP_MAX_LIMIT:
            raise HTTPException(status_code=409, detail=f"{CustomerException.VIP_MAX_LIMIT} - out of 10 customers limit")

        if result == CustomerException.CUSTOMER_NOT_FOUND:
            raise HTTPException(status_code=404, detail=f"{CustomerException.CUSTOMER_NOT_FOUND}")

    return result


@router.post("/create", status_code=201)
async def create_customer(customer: Customer) -> str:

    result: Union[int, CustomerException] = await customer_service.create_customer(customer)
    _exception_handler(result)

    return "customer created successfully"


@router.put("/update-{customer_id}",status_code=200)
async def update_customer_by_id(customer_id: int, customer: Customer) -> str:

    result: Union[str, CustomerException] = await customer_service.update_customer_by_id(customer_id, customer)
    final_result = _exception_handler(result)

    return final_result


@router.get("/get-{customer_id}", response_model=Customer, status_code=200)
async def get_customer_by_id(customer_id: int) -> Customer:

    result: Union[Customer, CustomerException] = await customer_service.get_customer_by_id(customer_id)
    final_result = _exception_handler(result)

    return final_result


@router.get("/get/all",response_model=List[Customer], status_code=200)
async def get_all_customers() -> List[Customer]:

    return await customer_service.get_all_customers()


@router.delete("/delete-{customer_id}", status_code=200)
async def delete_customer_by_id(customer_id: int) -> str:

    result: Union[str, CustomerException] = await customer_service.delete_customer_by_id(customer_id)
    final_result = _exception_handler(result)

    return final_result