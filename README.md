# Customer Micro Service

A small FastAPI micro service that manages **customers**, their **orders**, and their
**favorite items**. It is one half of a two-service learning project; it talks to the
companion [`sellers_micro_service`](https://github.com/IlaiTayar/sellers_micro_service)
over HTTP to resolve item prices, and it also demonstrates calling a public external API
(TVmaze).

> This is a personal learning project built to practice a layered micro service
> architecture (REST API + MySQL + Redis caching + inter-service calls). It is not meant
> for production use.

## Features

- CRUD for **customers**, with a VIP tier limited to 10 customers.
- CRUD for **orders**; on both creation and update the item name is validated against
  the seller service and the order price is set from the lowest-priced match. If the item
  name does not exist in the seller service the request is rejected (`404 ITEM_NOT_FOUND`)
  and no order is created or updated.
- CRUD for **customer favorite items**, validated against items in the seller service.
- A **TVmaze** proxy endpoint that fetches show details from the public TVmaze API.
- **Redis** caching for customer and favorite-item reads, with a configurable TTL.

## Tech stack

- Python 3.11+
- [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- [`databases`](https://www.encode.io/databases/) + `aiomysql` (async MySQL access)
- [Pydantic v2](https://docs.pydantic.dev/) + `pydantic-settings`
- [Redis](https://redis.io/) via `redis-py`
- [`httpx`](https://www.python-httpx.org/) for outbound HTTP calls

## Architecture

The service follows a clean, layered structure:

```
controller/   FastAPI routers (HTTP layer, request/response + error mapping)
service/      Business logic (validation, VIP rules, cross-service orchestration)
repository/   Data access (SQL queries + Redis cache)
model/        Pydantic models: base models, request/response models, domain exceptions
api/          Clients for external (TVmaze) and internal (seller service) APIs
config/       Settings loaded from environment variables
```

Services return either a value or a domain `*Exception` enum; the controllers translate
those enums into the appropriate HTTP status codes.

## Project layout

```
customer_micro_service/
├─ main.py                      # FastAPI app + startup/shutdown (lifespan)
├─ database.py                  # Async Database instance
├─ config/config.py             # Settings (env-driven)
├─ controller/                  # customer / order / favorite-item / tv_maze routers
├─ service/                     # business logic
├─ repository/                  # SQL + cache access
├─ model/                       # pydantic models + exception enums
├─ api/                         # external (tv_maze) + internal (seller) clients
├─ redisClient/redis_client.py  # Redis client
├─ resources/db-migrations/     # init.sql (schema + seed data)
├─ docker-compose.yml           # MySQL + Redis for local development
└─ requirements.txt
```

## Configuration

All settings have defaults and can be overridden with environment variables
(see `config/config.py`):

| Variable                  | Default                   | Description                         |
|---------------------------|---------------------------|-------------------------------------|
| `MYSQL_USER`              | `user`                    | MySQL user                          |
| `MYSQL_PASSWORD`          | `password`                | MySQL password                      |
| `MYSQL_HOST`              | `localhost`               | MySQL host                          |
| `MYSQL_PORT`              | `3306`                    | MySQL port                          |
| `MYSQL_DATABASE`          | `main`                    | Database name                       |
| `TV_MAZE_BASE_URL`        | `https://api.tvmaze.com`  | TVmaze API base URL                 |
| `SELLER_SERVICE_BASE_URL` | `http://localhost:8001`   | Base URL of the seller service      |
| `REDIS_HOST`              | `localhost`               | Redis host                          |
| `REDIS_PORT`              | `6379`                    | Redis port                          |
| `REDIS_TTL`               | `100`                     | Cache TTL in seconds                |

The SQLAlchemy-style `DATABASE_URL` is derived automatically from the `MYSQL_*` values.

## Getting started

### 1. Start MySQL and Redis

```bash
docker compose up -d
```

This starts a MySQL 8 instance on `3306` (seeded from `resources/db-migrations/init.sql`)
and a Redis instance on `6379`.

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the service

```bash
uvicorn main:app --reload --port 8000
```

Interactive API docs are then available at `http://localhost:8000/docs`.

> To exercise order creation and favorite items end-to-end, also run the
> `sellers_micro_service` on port `8001`.

## API overview

### Customers (`/customer`)

| Method | Path                        | Description                 |
|--------|-----------------------------|-----------------------------|
| POST   | `/customer/create`          | Create a customer           |
| PUT    | `/customer/update-{id}`     | Update a customer by id     |
| GET    | `/customer/get-{id}`        | Get a customer by id        |
| GET    | `/customer/get/all`         | List all customers          |
| DELETE | `/customer/delete-{id}`     | Delete a customer by id     |

### Orders (`/order`)

| Method | Path                     | Description              |
|--------|--------------------------|--------------------------|
| POST   | `/order/create`          | Create an order          |
| PUT    | `/order/update-{id}`     | Update an order by id    |
| GET    | `/order/get-{id}`        | Get an order by id       |
| GET    | `/order/get/all`         | List all orders          |
| DELETE | `/order/delete-{id}`     | Delete an order by id    |

### Favorite items (`/customer-favorite-item`)

| Method | Path                                         | Description                         |
|--------|----------------------------------------------|-------------------------------------|
| POST   | `/customer-favorite-item/create`             | Add a favorite item for a customer  |
| PUT    | `/customer-favorite-item/update-{id}`        | Update a favorite item by id        |
| GET    | `/customer-favorite-item/get-item-{id}`      | Get a favorite item by id           |
| GET    | `/customer-favorite-item/get-customer-{id}`  | Get a customer and their favorites  |
| DELETE | `/customer-favorite-item/delete-{id}`        | Delete a favorite item by id        |

> `GET /customer-favorite-item/get-customer-{id}` returns the customer **once**, followed
> by a flat list of their favorite items, instead of repeating the customer on every item:
>
> ```json
> {
>   "customer": { "customer_id": 1, "first_name": "Jane", "last_name": "Doe", "email": "jane@example.com", "status": "REGULAR" },
>   "favorite_items": [
>     { "favorite_item_id": 10, "item_response": { "item_id": 5, "seller_id": 1, "item_name": "Laptop", "price": 999.99 } }
>   ]
> }
> ```

### TVmaze (`/tv_maze`)

| Method | Path                          | Description                        |
|--------|-------------------------------|------------------------------------|
| GET    | `/tv_maze/get/show-{show_id}` | Fetch a TV show from the TVmaze API|

### Example

```bash
curl -X POST http://localhost:8000/customer/create \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Jane", "last_name": "Doe", "email": "jane@example.com", "status": "VIP"}'
```
