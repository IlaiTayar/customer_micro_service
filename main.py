from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from controller.order_controller import router as order_router
from controller.customer_controller import router as customer_router
from controller.item_controller import router as item_router
from controller.tv_maze_controller import router as tv_maze_router
from controller.customer_favorite_item_controller import router as favorite_item_router
from controller.auth_controller import router as auth_router
from database import database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await database.connect()
    print("Database connected")
    yield
    await database.disconnect()
    print("Database disconnected")


app: FastAPI = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(order_router)
app.include_router(customer_router)
app.include_router(item_router)
app.include_router(favorite_item_router)
app.include_router(tv_maze_router)
