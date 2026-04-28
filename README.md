# PetPal Backend

REST API for PetPal built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **Cloudinary**.

## Stack

- FastAPI + Uvicorn
- PostgreSQL + Alembic migrations
- JWT authentication
- Cloudinary for image uploads

## Setup

```bash
cd PetPal-backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env     # edit with your values
```

### Database

```bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
python -m app.seed.seed_db
```

### Run

```bash
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Environment variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key |
| `CORS_ORIGINS` | Allowed frontend origins |
| `CLOUDINARY_*` | Cloudinary credentials |

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Current user |
| GET | `/api/pets` | List user's pets |
| POST | `/api/pets` | Create pet (multipart) |
| GET | `/api/pets/{id}/photos` | Gallery |
| GET | `/api/pets/{id}/trackers/weight/chart` | Weight chart data |

Full docs at `/docs`.

## Deploy (Render / Railway)

1. Add PostgreSQL addon (Neon/Supabase also works)
2. Set all env vars from `.env.example`
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Run migrations on deploy: `alembic upgrade head && python -m app.seed.seed_db`
