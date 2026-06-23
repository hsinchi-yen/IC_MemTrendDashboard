@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ============================================================================
echo IC MemTrendDashboard - Docker Launcher
echo ============================================================================
echo.

REM Check Docker
docker --version >nul 2>&1 || (
    echo ERROR: Docker not found. Please install Docker Desktop.
    echo https://www.docker.com/products/docker-desktop
    exit /b 1
)

REM Check Docker daemon
docker ps >nul 2>&1 || (
    echo ERROR: Docker is not running. Please start Docker Desktop.
    exit /b 1
)

REM Create .env if missing
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env from .env.example...
        copy .env.example .env >nul
    ) else (
        echo ERROR: .env.example not found
        exit /b 1
    )
)

echo Starting Docker Compose...
echo.
echo Services:
echo   Frontend:     http://localhost:8510
echo   Backend API:  http://localhost:18000
echo   API Docs:     http://localhost:18000/docs
echo.

docker-compose up --build
