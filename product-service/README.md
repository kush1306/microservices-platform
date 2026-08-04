# Product Service

Production-ready Product Microservice built with FastAPI, SQLAlchemy, and Pydantic v2.

## Tech Stack

- Python 3.13
- FastAPI
- SQLAlchemy 2.x
- Pydantic v2
- SQLite (local development)
- python-dotenv

## Features

- Full CRUD APIs for products
- Unique SKU enforcement
- Search by product name
- Filter by category
- SQLAlchemy ORM with SQLite
- Pydantic v2 request/response validation
- Proper HTTP status codes and validation errors
- Structured logging
- CORS middleware
- Environment-based configuration (`DATABASE_URL` required)
- Clean separation of routes and business logic

## Project Structure

```
product-service/
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
cd product-service
py -3.13 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
```

## Setup (Linux / macOS)

```bash
cd product-service
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
| GET | `/products` | List products (`skip`, `limit`) | 200 |
| GET | `/products/{id}` | Get product by id | 200 / 404 |
| POST | `/products` | Create product | 201 / 409 / 422 |
| PUT | `/products/{id}` | Update product | 200 / 404 / 409 / 422 |
| DELETE | `/products/{id}` | Delete product | 200 / 404 |
| GET | `/products/search?name=` | Search products by name | 200 / 422 |
| GET | `/products/category/{category}` | List products by category | 200 |

## Product Fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | Auto-generated primary key |
| `name` | string | Required, 1–200 chars |
| `description` | string | Required |
| `category` | string | Required, 1–100 chars |
| `price` | decimal | Required, must be > 0 |
| `quantity` | int | Required, must be >= 0 |
| `sku` | string | Required, unique |
| `image_url` | string | Optional URL |
| `created_at` | datetime | Set on create |
| `updated_at` | datetime | Updated on change |

## Example Requests

### Create product

```bash
curl -X POST http://127.0.0.1:8000/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse with USB receiver",
    "category": "Electronics",
    "price": 29.99,
    "quantity": 150,
    "sku": "ELEC-MOUSE-001",
    "image_url": "https://example.com/images/mouse.jpg"
  }'
```

### List products

```bash
curl http://127.0.0.1:8000/products
```

### Get product

```bash
curl http://127.0.0.1:8000/products/1
```

### Search by name

```bash
curl "http://127.0.0.1:8000/products/search?name=mouse"
```

### Filter by category

```bash
curl http://127.0.0.1:8000/products/category/Electronics
```

### Update product

```bash
curl -X PUT http://127.0.0.1:8000/products/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wireless Mouse Pro",
    "description": "Updated ergonomic wireless mouse",
    "category": "Electronics",
    "price": 34.99,
    "quantity": 120,
    "sku": "ELEC-MOUSE-001",
    "image_url": "https://example.com/images/mouse-pro.jpg"
  }'
```

### Delete product

```bash
curl -X DELETE http://127.0.0.1:8000/products/1
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | *(required)* | SQLAlchemy database URL, e.g. `sqlite:///./products.db` |
| `APP_NAME` | `Product Service` | Service display name |
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
