# User Service

Production-ready User Microservice built with FastAPI, SQLAlchemy, and Pydantic v2.

## Tech Stack

- Python 3.13
- FastAPI
- SQLAlchemy 2.x
- Pydantic v2
- SQLite (local development)
- python-dotenv

## Features

- Full CRUD APIs for users
- SQLAlchemy ORM with SQLite
- Pydantic v2 request/response validation
- Proper HTTP status codes and validation errors
- Structured logging
- CORS middleware
- Environment-based configuration (`DATABASE_URL` required)
- Clean separation of routes and business logic

## Project Structure

```
user-service/
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
cd user-service
py -3.13 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
```

## Setup (Linux / macOS)

```bash
cd user-service
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
| GET | `/users` | List users (`skip`, `limit`) | 200 |
| GET | `/users/{id}` | Get user by id | 200 / 404 |
| POST | `/users` | Create user | 201 / 409 / 422 |
| PUT | `/users/{id}` | Update user | 200 / 404 / 409 / 422 |
| DELETE | `/users/{id}` | Delete user | 200 / 404 |

## Example Requests

### Create user

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","username":"alice","full_name":"Alice","phone":"+1234567890"}'
```

### List users

```bash
curl http://127.0.0.1:8000/users
```

### Get user

```bash
curl http://127.0.0.1:8000/users/1
```

### Update user

```bash
curl -X PUT http://127.0.0.1:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","username":"alice","full_name":"Alice Updated","phone":"+1234567890","is_active":true}'
```

### Delete user

```bash
curl -X DELETE http://127.0.0.1:8000/users/1
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | *(required)* | SQLAlchemy database URL, e.g. `sqlite:///./users.db` |
| `APP_NAME` | `User Service` | Service display name |
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
