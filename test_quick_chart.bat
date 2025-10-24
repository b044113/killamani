@echo off
REM Script para probar la funcionalidad Quick Chart en Windows
REM Uso: test_quick_chart.bat

echo ==========================================
echo Quick Chart MVP - Test Suite
echo ==========================================
echo.

echo 1. Verificando que el backend esta corriendo...
docker ps | findstr killamani-backend-dev >nul
if %errorlevel% equ 0 (
    echo [OK] Backend esta corriendo
) else (
    echo [ERROR] Backend NO esta corriendo
    echo Ejecuta: docker-compose -f docker-compose.dev.yml up -d
    exit /b 1
)

echo.
echo 2. Ejecutando tests unitarios del Use Case...
docker exec killamani-backend-dev pytest backend/tests/unit/test_quick_calculate_chart_use_case.py -v --tb=short
if %errorlevel% equ 0 (
    echo [OK] Tests del Use Case pasaron
) else (
    echo [ERROR] Tests del Use Case fallaron
)

echo.
echo 3. Ejecutando tests unitarios del Calculator SVG...
docker exec killamani-backend-dev pytest backend/tests/unit/test_kerykeion_calculator_svg.py -v --tb=short
if %errorlevel% equ 0 (
    echo [OK] Tests del Calculator SVG pasaron
) else (
    echo [ERROR] Tests del Calculator SVG fallaron
)

echo.
echo 4. Ejecutando tests E2E del endpoint...
docker exec killamani-backend-dev pytest backend/tests/e2e/test_quick_chart_endpoint.py -v --tb=short
if %errorlevel% equ 0 (
    echo [OK] Tests E2E pasaron
) else (
    echo [ERROR] Tests E2E fallaron
)

echo.
echo 5. Generando reporte de cobertura...
docker exec killamani-backend-dev pytest backend/tests/unit/test_quick_calculate_chart_use_case.py backend/tests/unit/test_kerykeion_calculator_svg.py backend/tests/e2e/test_quick_chart_endpoint.py --cov=backend/src --cov-report=term --cov-report=html -q

echo.
echo 6. Probando endpoint manualmente...
curl -s -X POST http://localhost:8000/api/charts/quick-calculate -H "Content-Type: application/json" -d "{\"name\":\"Test User\",\"birth_date\":\"1990-04-15\",\"birth_time\":\"14:30\",\"birth_city\":\"New York\",\"birth_country\":\"US\",\"birth_timezone\":\"America/New_York\",\"house_system\":\"placidus\",\"language\":\"en\"}" > response.json

if exist response.json (
    echo [OK] Endpoint respondio correctamente
    echo Respuesta guardada en response.json
) else (
    echo [ERROR] El endpoint no respondio
)

echo.
echo ==========================================
echo Resumen de Tests
echo ==========================================
echo.
echo [OK] Endpoint: http://localhost:8000/api/charts/quick-calculate
echo [OK] Docs: http://localhost:8000/docs
echo [OK] Response: response.json
echo.
echo Para ver la documentacion interactiva:
echo   start http://localhost:8000/docs
echo.
echo Para ver el response JSON:
echo   type response.json
echo.
echo [OK] Todos los tests completados!
pause
