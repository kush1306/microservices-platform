# Inventory Service

Production-ready Inventory Microservice built with FastAPI, SQLAlchemy, and Pydantic v2.

## Tech Stack

- Python 3.13
- FastAPI
- SQLAlchemy 2.x
- Pydantic v2
- SQLite (local development)
- python-dotenv

## Features

- Full CRUD APIs for inventory stock
- Stock increase / decrease operations
- Reserve and release stock with availability checks
- Lookup by product id
- Unique SKU enforcement
- SQLAlchemy ORM with SQLite
- Pydantic v2 request/response validation
- Proper HTTP status codes and validation errors
- Structured logging
- CORS middleware
- Environment-based configuration (`DATABASE_URL` required)
- Clean separation of routes and business logic

## Project Structure

```
inventory-service/
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI entrypoint
│   ├── config.py      # Settings via python-dotenv
│   ├── database.py    # SQLAlchemy engine/session
│   ├── models.py      # ORM models
│   ├── schemas.py     # Pydantic schemas
│   ├── routes.py      # API routes
│   ├── services.py    # Business logic
│   └── utils.py       # Helpers and logging
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
└── .python-version
```

## Requirements

- Python 3.13
- pip

## Setup (Windows / Git Bash)

```bash
cd inventory-service
py -3.13 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
```

## Setup (Linux / macOS)

```bash
cd inventory-service
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload
```

- Swagger UI: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## API Endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | `/health` | Health check | 200 |
| GET | `/inventory` | List inventory (`skip`, `limit`) | 200 |
| GET | `/inventory/{id}` | Get inventory by id | 200 / 404 |
| GET | `/inventory/product/{product_id}` | List inventory by product | 200 |
| POST | `/inventory` | Create inventory | 201 / 409 / 422 |
| PUT | `/inventory/{id}` | Update inventory | 200 / 404 / 409 / 422 |
| DELETE | `/inventory/{id}` | Delete inventory | 200 / 404 |
| PATCH | `/inventory/{id}/increase` | Increase stock | 200 / 404 / 422 |
| PATCH | `/inventory/{id}/decrease` | Decrease stock | 200 / 400 / 404 / 422 |
| PATCH | `/inventory/{id}/reserve` | Reserve stock | 200 / 400 / 404 / 422 |
| PATCH | `/inventory/{id}/release` | Release reserved stock | 200 / 400 / 404 / 422 |

## Inventory Fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | Auto-generated primary key |
| `product_id` | int | Required, must be > 0 |
| `sku` | string | Required, unique |
| `quantity` | int | Required, must be >= 0 |
| `reserved_quantity` | int | Required, must be >= 0 and <= quantity |
| `warehouse` | string | Required, 1–100 chars |
| `low_stock_threshold` | int | Required, must be >= 0 (default 10) |
| `created_at` | datetime | Set on create |
| `updated_at` | datetime | Updated on change |

## Validation Rules

- `quantity >= 0`
- `reserved_quantity >= 0`
- Cannot reserve more than available stock (`quantity - reserved_quantity`)
- Cannot decrease below reserved stock
- Cannot release more than currently reserved

## Example Requests

### Create inventory

```bash
curl -X POST http://127.0.0.1:8000/inventory \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "sku": "ELEC-MOUSE-001",
    "quantity": 150,
    "reserved_quantity": 0,
    "warehouse": "WH-EAST",
    "low_stock_threshold": 20
  }'
```

### List inventory

```bash
curl http://127.0.0.1:8000/inventory
```

### Get inventory

```bash
curl http://127.0.0.1:8000/inventory/1
```

### List by product

```bash
curl http://127.0.0.1:8000/inventory/product/1
```

### Increase stock

```bash
curl -X PATCH http://127.0.0.1:8000/inventory/1/increase \
  -H "Content-Type: application/json" \
  -d '{"amount": 25}'
```

### Reserve stock

```bash
curl -X PATCH http://127.0.0.1:8000/inventory/1/reserve \
  -H "Content-Type: application/json" \
  -d '{"amount": 5}'
```

### Delete inventory

```bash
curl -X DELETE http://127.0.0.1:8000/inventory/1
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | *(required)* | SQLAlchemy database URL, e.g. `sqlite:///./inventory.db` |
| `APP_NAME` | `Inventory Service` | Service display name |
| `APP_VERSION` | `1.0.0` | Service version |
| `DEBUG` | `false` | Debug flag |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |
| `HOST` | `0.0.0.0` | Bind host |
| `PORT` | `8000` | Bind port |

## Notes

- Dependencies in `requirements.txt` are pinned to versions compatible with Python 3.13.
- SQLite is used for local development so no external database install is required.
- Do not commit `.env` or `*.db` files.
