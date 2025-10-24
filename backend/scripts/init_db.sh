#!/bin/bash
# Database Initialization Script
# This script runs migrations and seeds initial data

set -e

echo "==========================================="
echo "Database Initialization Script"
echo "==========================================="
echo ""

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h postgres -U killamani > /dev/null 2>&1; do
    echo "  PostgreSQL is unavailable - sleeping"
    sleep 2
done
echo "  PostgreSQL is ready!"
echo ""

# Run migrations
echo "Running database migrations..."
cd /app
alembic upgrade head
echo "  Migrations completed!"
echo ""

# Seed initial data
echo "Seeding initial data..."
python backend/scripts/seed_data.py
echo "  Seeding completed!"
echo ""

echo "==========================================="
echo "Database initialization completed!"
echo "==========================================="
echo ""
echo "Available users:"
echo "  Admin:      admin@astrojoy.com / Admin123!"
echo "  Consultant: consultant@astrojoy.com / Consultant123!"
echo ""
