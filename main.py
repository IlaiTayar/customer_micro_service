from fastapi import FastAPI
from controller.order_controller import router as order_router
from controller.customer_controller import router as customer_router
from controller.tv_maze_controller import router as tv_maze_router
from database import database


app: FastAPI = FastAPI()

app.include_router(order_router)
app.include_router(customer_router)
app.include_router(tv_maze_router)


@app.on_event("startup")
async def startup():
    await database.connect()
    print("Database connected")


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("Database disconnected")