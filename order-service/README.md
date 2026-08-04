# Order Service

Production-ready Order Microservice built with FastAPI, SQLAlchemy, and Pydantic v2.

## Tech Stack

- Python 3.13
- FastAPI
- SQLAlchemy 2.x
- Pydantic v2
- SQLite (local development)
- python-dotenv

## Features

- Full CRUD APIs for customer orders
- Automatic `total_price = quantity × unit_price` calculation
- Order status transitions (`PENDING`, `CONFIRMED`, `SHIPPED`, `DELIVERED`, `CANCELLED`)
- Lookup by user id
- SQLAlchemy ORM with SQLite
- Pydantic v2 request/response validation
- Proper HTTP status codes and validation errors
- Structured logging
- CORS middleware
- Environment-based configuration (`DATABASE_URL` required)
- Clean separation of routes and business logic

## Project Structure

```
order-service/
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
cd order-service
py -3.13 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
```

## Setup (Linux / macOS)

```bash
cd order-service
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
| GET | `/orders` | List orders (`skip`, `limit`) | 200 |
| GET | `/orders/{id}` | Get order by id | 200 / 404 |
| GET | `/orders/user/{user_id}` | List orders by user | 200 |
| POST | `/orders` | Create order | 201 / 422 |
| PUT | `/orders/{id}` | Update order | 200 / 404 / 422 |
| PATCH | `/orders/{id}/status` | Update order status | 200 / 404 / 422 |
| DELETE | `/orders/{id}` | Delete order | 200 / 404 |

## Order Fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | Auto-generated primary key |
| `user_id` | int | Required, must be > 0 |
| `product_id` | int | Required, must be > 0 |
| `quantity` | int | Required, must be > 0 |
| `unit_price` | decimal | Required, must be > 0 |
| `total_price` | decimal | Computed as quantity × unit_price |
| `status` | string | One of `PENDING`, `CONFIRMED`, `SHIPPED`, `DELIVERED`, `CANCELLED` |
| `created_at` | datetime | Set on create |
| `updated_at` | datetime | Updated on change |

## Business Rules

- `total_price = quantity × unit_price` (computed server-side)
- `quantity > 0`
- `unit_price > 0`
- Status must be one of the allowed enum values

## Example Requests

### Create order

```bash
curl -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "product_id": 1,
    "quantity": 2,
    "unit_price": 29.99,
    "status": "PENDING"
  }'
```

### List orders

```bash
curl http://127.0.0.1:8000/orders
```

### Get order

```bash
curl http://127.0.0.1:8000/orders/1
```

### List by user

```bash
curl http://127.0.0.1:8000/orders/user/1
```

### Update status

```bash
curl -X PATCH http://127.0.0.1:8000/orders/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "CONFIRMED"}'
```

### Delete order

```bash
curl -X DELETE http://127.0.0.1:8000/orders/1
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | *(required)* | SQLAlchemy database URL, e.g. `sqlite:///./orders.db` |
| `APP_NAME` | `Order Service` | Service display name |
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
