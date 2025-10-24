#!/bin/bash
# Backend Entrypoint Script
# Initializes database and starts the FastAPI server

set -e

echo "Starting Killamani Backend..."
echo ""

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
until pg_isready -h postgres -U killamani > /dev/null 2>&1; do
    echo "  Waiting for database..."
    sleep 2
done
echo "  Database is ready!"
echo ""

# Run migrations
echo "Running migrations..."
alembic upgrade head
echo "  Migrations completed!"
echo ""

# Seed data (only if tables are empty)
echo "Checking if seed data is needed..."
python -c "
from src.infrastructure.database.connection import get_db_context
from src.infrastructure.database.models import UserModel
try:
    with get_db_context() as db:
        user_count = db.query(UserModel).count()
        if user_count == 0:
            print('  No users found, seeding data...')
            exit(0)
        else:
            print(f'  Found {user_count} users, skipping seed')
            exit(1)
except Exception as e:
    print(f'  Error checking users: {e}')
    exit(0)
" && python scripts/seed_data.py || echo "  Seed data skipped"
echo ""

# Start the server
echo "Starting FastAPI server..."
echo ""
exec "$@"
