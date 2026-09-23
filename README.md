first_serverA:

lightweight FastAPI service with aiomysql for async MySQL access,
Redis as a cache layer, all containerized with Docker and orchestrated via docker‑compose.

Features:

- FastAPI: Building blocks for async REST endpoints.
- aiomysql + databases: Async MySQL driver.
- Redis: Simple key‑value cache (e.g., customer lookup).
- Docker / docker‑compose: Reproducible environment, zero‑config deployment.
- Layered architecture: controller, repository, service – keeps business logic testable.

Quick start:

# Clone
git clone https://github.com/IlaiTayar/first_server.git
cd first_server

# ── Optionally create a virtual env ──
python -m venv .venv
source .venv\Scripts\activate   # apple: .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run locally (no Docker)
uvicorn main:app --reload

Docker:

# Build & start services
docker compose up -d

# Stop
docker compose down 

The API will be available at http://localhost:8000.

API reference:

HTTP,Path,Description
POST /customers/,"Create a new customer. Body: {first_name, last_name, email}.",
GET /customers/{id},Retrieve customer by ID.,
GET /orders/,List all orders for the authenticated customer (via customer_id query).,
POST /orders/,Create an order for a customer.,

All endpoints return JSON; see the OpenAPI docs at http://localhost:8000/docs.

Architecture overview:
- The controller layers expose the HTTP routes.
- The repository performs async DB queries and caches results with Redis.
- Redis is configured in config/config.py (TTL = 100 s).
- Docker volumes expose MySQL data persistently; the API container uses the same network as the DB and cache.

Configuration:

All settings live in config/config.py. Override them with environment variables:

MYSQL_HOST=mysql,
MYSQL_USER=root,
MYSQL_PASSWORD=secret,
MYSQL_DATABASE=main,
REDIS_HOST=redis,
REDIS_PORT=6379

Testing:

pytest -v

(You’ll need pytest-asyncio and httpx in dev dependencies.)

LicenseMIT © 2026 IlaiTayar
