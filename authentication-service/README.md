# Authentication Service

JWT-based authentication microservice for the microservices platform.

## Features

- User registration and login
- Access and refresh JWT tokens
- Token refresh with rotation
- Logout (refresh token revocation)
- Current user profile read/update
- Health check endpoint
- SQLite by default; PostgreSQL-ready via `DATABASE_URL`

## Project Structure

```
authentication-service/
├── app/
│   ├── main.py        # FastAPI application entrypoint
│   ├── config.py      # Settings from environment variables
│   ├── database.py    # SQLAlchemy engine and session
│   ├── models.py      # ORM models (User, RefreshToken)
│   ├── schemas.py     # Pydantic request/response schemas
│   ├── security.py    # Password hashing and JWT helpers
│   ├── auth.py        # Auth business logic and dependencies
│   ├── routes.py      # API route handlers
│   └── utils.py       # Shared helpers
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Requirements

- Python 3.11+
- pip

## Setup

```bash
cd authentication-service
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set a strong `SECRET_KEY` before deploying.

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

## API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/` | Service metadata | No |
| GET | `/api/v1/health` | Health check | No |
| POST | `/api/v1/auth/register` | Register a user | No |
| POST | `/api/v1/auth/login` | Login (OAuth2 password form) | No |
| POST | `/api/v1/auth/refresh` | Refresh tokens | No |
| POST | `/api/v1/auth/logout` | Revoke refresh token | Bearer |
| GET | `/api/v1/users/me` | Current user profile | Bearer |
| PATCH | `/api/v1/users/me` | Update current user | Bearer |

## Example Usage

### Register

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","username":"alice","password":"secret123","full_name":"Alice"}'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret123"
```

### Current User

```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

### Refresh

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./auth.db` | SQLAlchemy database URL |
| `SECRET_KEY` | (dev default) | JWT signing key |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |
| `API_PREFIX` | `/api/v1` | API route prefix |
