#!/bin/bash

# AstroJoy Platform - Development Startup Script

set -e  # Exit on error

echo "🚀 Starting AstroJoy Platform Development Environment..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env created. Please edit it with your configuration."
    echo ""
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "🐳 Docker is running..."
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.dev.yml down
echo ""

# Build images
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.dev.yml build
echo ""

# Start containers
echo "▶️  Starting containers..."
docker-compose -f docker-compose.dev.yml up -d postgres redis
echo "⏳ Waiting for database to be ready..."
sleep 5
echo ""

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.dev.yml run --rm backend alembic upgrade head || echo "⚠️  Migrations not yet created. Run 'alembic init migrations' first."
echo ""

# Start all services
echo "🚀 Starting all services..."
docker-compose -f docker-compose.dev.yml up -d
echo ""

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10
echo ""

# Show status
echo "📊 Container Status:"
docker-compose -f docker-compose.dev.yml ps
echo ""

# Show URLs
echo "✅ AstroJoy Platform is running!"
echo ""
echo "📍 Access Points:"
echo "   Frontend:       http://localhost:3000"
echo "   Backend API:    http://localhost:8000"
echo "   API Docs:       http://localhost:8000/docs"
echo "   API ReDoc:      http://localhost:8000/redoc"
echo "   PostgreSQL:     localhost:5432"
echo "   Redis:          localhost:6379"
echo ""
echo "🔧 Optional Tools (start with --profile tools):"
echo "   PgAdmin:        http://localhost:5050 (admin@astrojoy.com / admin)"
echo "   Redis Commander: http://localhost:8081"
echo "   Mailhog:        http://localhost:8025"
echo ""
echo "📝 Useful Commands:"
echo "   View logs:          docker-compose -f docker-compose.dev.yml logs -f"
echo "   Stop all:           docker-compose -f docker-compose.dev.yml down"
echo "   Restart backend:    docker-compose -f docker-compose.dev.yml restart backend"
echo "   Run tests:          docker-compose -f docker-compose.dev.yml exec backend pytest"
echo ""
echo "🎉 Happy coding!"
