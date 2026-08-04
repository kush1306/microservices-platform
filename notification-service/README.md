# Notification Service

Production-ready Notification Microservice built with FastAPI, SQLAlchemy, and Pydantic v2.

## Tech Stack

- Python 3.13
- FastAPI
- SQLAlchemy 2.x
- Pydantic v2
- SQLite (local development)
- python-dotenv

## Features

- Store notifications in the database (no external email/SMS provider)
- Support for `EMAIL`, `SMS`, and `PUSH` notification types
- Mark notifications as read
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
notification-service/
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
cd notification-service
py -3.13 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
```

## Setup (Linux / macOS)

```bash
cd notification-service
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
| GET | `/notifications` | List notifications (`skip`, `limit`) | 200 |
| GET | `/notifications/{id}` | Get notification by id | 200 / 404 |
| GET | `/notifications/user/{user_id}` | List notifications by user | 200 |
| POST | `/notifications` | Create notification | 201 / 422 |
| PATCH | `/notifications/{id}/read` | Mark as read | 200 / 404 |
| DELETE | `/notifications/{id}` | Delete notification | 200 / 404 |

## Notification Fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | Auto-generated primary key |
| `user_id` | int | Required, must be > 0 |
| `title` | string | Required, 1–200 chars |
| `message` | string | Required |
| `type` | string | One of `EMAIL`, `SMS`, `PUSH` |
| `is_read` | bool | Defaults to `false` on create |
| `created_at` | datetime | Set on create |

## Example Requests

### Create notification

```bash
curl -X POST http://127.0.0.1:8000/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "title": "Order Confirmed",
    "message": "Your order #42 has been confirmed.",
    "type": "EMAIL"
  }'
```

### List notifications

```bash
curl http://127.0.0.1:8000/notifications
```

### Get notification

```bash
curl http://127.0.0.1:8000/notifications/1
```

### List by user

```bash
curl http://127.0.0.1:8000/notifications/user/1
```

### Mark as read

```bash
curl -X PATCH http://127.0.0.1:8000/notifications/1/read
```

### Delete notification

```bash
curl -X DELETE http://127.0.0.1:8000/notifications/1
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | *(required)* | SQLAlchemy database URL, e.g. `sqlite:///./notifications.db` |
| `APP_NAME` | `Notification Service` | Service display name |
| `APP_VERSION` | `1.0.0` | Service version |
| `DEBUG` | `false` | Debug flag |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |
| `HOST` | `0.0.0.0` | Bind host |
| `PORT` | `8000` | Bind port |

## Notes

- Dependencies in `requirements.txt` are pinned to versions compatible with Python 3.13.
- SQLite is used for local development so no external database install is required.
- Notifications are stored in the database only; no real email/SMS/push provider is integrated.
- Do not commit `.env` or `*.db` files.
