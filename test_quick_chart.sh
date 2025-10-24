#!/bin/bash

# Script para probar la funcionalidad Quick Chart
# Uso: ./test_quick_chart.sh

set -e

echo "=========================================="
echo "Quick Chart MVP - Test Suite"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir en verde
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Función para imprimir en rojo
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Función para imprimir en amarillo
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

echo "1. Verificando que el backend está corriendo..."
if docker ps | grep -q killamani-backend-dev; then
    print_success "Backend está corriendo"
else
    print_error "Backend NO está corriendo"
    echo "Ejecuta: docker-compose -f docker-compose.dev.yml up -d"
    exit 1
fi

echo ""
echo "2. Ejecutando tests unitarios del Use Case..."
docker exec killamani-backend-dev pytest backend/tests/unit/test_quick_calculate_chart_use_case.py -v --tb=short
if [ $? -eq 0 ]; then
    print_success "Tests del Use Case pasaron"
else
    print_error "Tests del Use Case fallaron"
fi

echo ""
echo "3. Ejecutando tests unitarios del Calculator SVG..."
docker exec killamani-backend-dev pytest backend/tests/unit/test_kerykeion_calculator_svg.py -v --tb=short
if [ $? -eq 0 ]; then
    print_success "Tests del Calculator SVG pasaron"
else
    print_error "Tests del Calculator SVG fallaron"
fi

echo ""
echo "4. Ejecutando tests E2E del endpoint..."
docker exec killamani-backend-dev pytest backend/tests/e2e/test_quick_chart_endpoint.py -v --tb=short
if [ $? -eq 0 ]; then
    print_success "Tests E2E pasaron"
else
    print_error "Tests E2E fallaron"
fi

echo ""
echo "5. Generando reporte de cobertura..."
docker exec killamani-backend-dev pytest \
    backend/tests/unit/test_quick_calculate_chart_use_case.py \
    backend/tests/unit/test_kerykeion_calculator_svg.py \
    backend/tests/e2e/test_quick_chart_endpoint.py \
    --cov=backend/src \
    --cov-report=term \
    --cov-report=html \
    -q

echo ""
echo "6. Probando endpoint manualmente..."

# Test básico
response=$(curl -s -X POST http://localhost:8000/api/charts/quick-calculate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "birth_date": "1990-04-15",
    "birth_time": "14:30",
    "birth_city": "New York",
    "birth_country": "US",
    "birth_timezone": "America/New_York",
    "house_system": "placidus",
    "language": "en"
  }')

if echo "$response" | jq -e '.sun_sign' > /dev/null 2>&1; then
    sun_sign=$(echo "$response" | jq -r '.sun_sign')
    print_success "Endpoint funciona correctamente - Sun Sign: $sun_sign"

    # Guardar SVG
    echo "$response" | jq -r '.svg_data' > test_chart.svg
    print_success "SVG guardado en test_chart.svg"
else
    print_error "El endpoint no respondió correctamente"
    echo "Response: $response"
fi

echo ""
echo "=========================================="
echo "Resumen de Tests"
echo "=========================================="
echo ""

# Contar tests
total_tests=$(docker exec killamani-backend-dev pytest \
    backend/tests/unit/test_quick_calculate_chart_use_case.py \
    backend/tests/unit/test_kerykeion_calculator_svg.py \
    backend/tests/e2e/test_quick_chart_endpoint.py \
    --collect-only -q | grep "test" | wc -l)

print_success "Total de tests: $total_tests"
print_success "Endpoint: http://localhost:8000/api/charts/quick-calculate"
print_success "Docs: http://localhost:8000/docs"
print_success "SVG generado: test_chart.svg"

echo ""
echo "Para ver el reporte de cobertura HTML:"
echo "  docker exec killamani-backend-dev cat htmlcov/index.html"
echo ""
echo "Para abrir el SVG generado:"
echo "  start test_chart.svg  # Windows"
echo "  open test_chart.svg   # Mac"
echo "  xdg-open test_chart.svg  # Linux"
echo ""

print_success "¡Todos los tests completados!"
