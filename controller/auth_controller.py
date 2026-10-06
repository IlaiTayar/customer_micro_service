from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from model.base_models.customer import Customer, CustomerStatus
from model.exception_handler_model.customer_exception import CustomerException
from security.auth import (
    Principal,
    ROLE_ADMIN,
    ROLE_CUSTOMER,
    create_access_token,
    get_current_principal,
    is_admin,
)
from service import customer_service

router: APIRouter = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    customer_id: int
    email: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    customer_id: int
    first_name: str
    last_name: str
    role: str


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    status: Optional[str] = "REGULAR"


class MeResponse(BaseModel):
    principal_id: int
    role: str


@router.post("/login", response_model=LoginResponse, status_code=200)
async def login(login_request: LoginRequest) -> LoginResponse:
    result: Union[Customer, CustomerException] = await customer_service.get_customer_by_id(login_request.customer_id)

    if isinstance(result, CustomerException):
        raise HTTPException(status_code=401, detail="Invalid customer id or email")

    if result.email.strip().lower() != login_request.email.strip().lower():
        raise HTTPException(status_code=401, detail="Invalid customer id or email")

    role = ROLE_ADMIN if is_admin(result.customer_id, result.email) else ROLE_CUSTOMER

    token = create_access_token(result.customer_id, role)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        customer_id=result.customer_id,
        first_name=result.first_name,
        last_name=result.last_name,
        role=role,
    )


@router.get("/me", response_model=MeResponse, status_code=200)
async def me(principal: Principal = Depends(get_current_principal)) -> MeResponse:
    return MeResponse(principal_id=principal.principal_id, role=principal.role)


@router.post("/register", response_model=LoginResponse, status_code=201)
async def register(register_request: RegisterRequest) -> LoginResponse:
    try:
        status = CustomerStatus(register_request.status or "REGULAR")
    except ValueError:
        status = CustomerStatus.REGULAR

    new_customer = Customer(
        first_name=register_request.first_name,
        last_name=register_request.last_name,
        email=register_request.email,
        status=status,
    )

    result: Union[int, CustomerException] = await customer_service.create_customer(new_customer)

    if result == CustomerException.CUSTOMER_EXISTS:
        raise HTTPException(status_code=409, detail="A customer with this email already exists")
    if result == CustomerException.VIP_MAX_LIMIT:
        raise HTTPException(status_code=409, detail="VIP customer limit reached")

    created: Union[Customer, CustomerException] = await customer_service.get_customer_by_email(register_request.email)
    if isinstance(created, CustomerException):
        raise HTTPException(status_code=500, detail="Registration failed")

    role = ROLE_ADMIN if is_admin(created.customer_id, created.email) else ROLE_CUSTOMER
    token = create_access_token(created.customer_id, role)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        customer_id=created.customer_id,
        first_name=created.first_name,
        last_name=created.last_name,
        role=role,
    )
