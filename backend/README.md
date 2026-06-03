# Agently Backend

FastAPI backend for the Agently MVP.

## Local Docker Run

```bash
docker compose up --build
```

API:

```text
http://localhost:8000
```

Health check:

```text
GET /health
```

## Database

Run migrations from inside the backend container:

```bash
alembic upgrade head
```

Seed the three MVP agents:

```bash
python scripts/seed_agents.py
```

