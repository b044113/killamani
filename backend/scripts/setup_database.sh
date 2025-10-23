#!/bin/bash
# AstroJoy Database Setup Script
# Sets up PostgreSQL databases for development and testing

set -e

echo "🚀 AstroJoy Database Setup"
echo "=============================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"

# Navigate to project root
cd "$(dirname "$0")/../.."

# Start PostgreSQL container
echo "📦 Starting PostgreSQL container..."
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker exec astrojoy-postgres pg_isready -U astrojoy > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Timeout waiting for PostgreSQL"
        exit 1
    fi
    sleep 1
done

# Create test database if it doesn't exist
echo "📊 Creating test database..."
docker exec astrojoy-postgres psql -U astrojoy -tc "SELECT 1 FROM pg_database WHERE datname = 'astrojoy_test'" | grep -q 1 || \
docker exec astrojoy-postgres psql -U astrojoy -c "CREATE DATABASE astrojoy_test;"

echo "✅ Test database ready"

# Run migrations on development database
echo "🔄 Running migrations on development database..."
cd backend
export DATABASE_URL="${DATABASE_URL:-postgresql://astrojoy:astrojoy2024@localhost:5432/astrojoy}"
alembic upgrade head

# Run migrations on test database
echo "🔄 Running migrations on test database..."
export DATABASE_URL="postgresql://astrojoy:astrojoy2024@localhost:5432/astrojoy_test"
alembic upgrade head

echo ""
echo "✅ Database setup complete!"
echo ""
echo "📝 Next steps:"
echo "   • Run tests: pytest -v"
echo "   • Start backend: uvicorn src.main:app --reload"
echo "   • Check coverage: pytest --cov=src --cov-report=html"
echo ""
