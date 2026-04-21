#!/usr/bin/env bash
set -euo pipefail

python -c "import time,os; print('Starting backend')"

# Wait for Postgres
python - <<'PY'
import os, time
import psycopg2
from urllib.parse import urlparse

url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/smart_cookbook')
parsed = urlparse(url)
for i in range(60):
    try:
        conn = psycopg2.connect(
            dbname=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
        )
        conn.close()
        print('DB ready')
        break
    except Exception as e:
        print('Waiting for DB...', i)
        time.sleep(1)
else:
    raise SystemExit('DB not ready')
PY

# Run migrations
alembic upgrade head

# Seed recipes if empty
python - <<'PY'
from app.core.database import SessionLocal
from app.seed.seed_recipes import seed_if_empty

db = SessionLocal()
try:
    created = seed_if_empty(db)
    print(f'Seeded recipes: {created}')
finally:
    db.close()
PY

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
