#!/bin/sh
set -e

echo "Waiting for database to be ready..."
# Basit retry - DB hazır olana kadar bekle
# Compose'da depends_on healthcheck zaten halleder, ama dayanıklılık için ekliyoruz
until python -c "
import asyncio
import asyncpg
import os

async def check():
    conn = await asyncpg.connect(
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME'],
        host=os.environ['DB_HOST'],
        port=int(os.environ.get('DB_PORT', 5432)),
    )
    await conn.close()

asyncio.run(check())
" 2>/dev/null; do
    echo "Database not ready, waiting 2 seconds..."
    sleep 2
done

echo "Database is ready. Running migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000