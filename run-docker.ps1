# ============================================================================
# IC MemTrendDashboard — Docker Compose Launcher (PowerShell)
# ============================================================================
# 
# Usage: 
#   PowerShell -ExecutionPolicy Bypass -File run-docker.ps1
#   Or in PowerShell: .\run-docker.ps1
#
# ============================================================================

param(
    [switch]$NoPrompt = $false
)

$ErrorActionPreference = "Stop"

# Colors
$Green = [System.ConsoleColor]::Green
$Red = [System.ConsoleColor]::Red
$Yellow = [System.ConsoleColor]::Yellow
$Cyan = [System.ConsoleColor]::Cyan

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    switch ($Type) {
        "Success" { Write-Host "✓ $Message" -ForegroundColor $Green }
        "Error" { Write-Host "✗ $Message" -ForegroundColor $Red }
        "Warning" { Write-Host "⚠ $Message" -ForegroundColor $Yellow }
        default { Write-Host "» $Message" -ForegroundColor $Cyan }
    }
}

function Check-Docker {
    try {
        $version = docker --version 2>&1
        Write-Status "Docker is installed: $version" "Success"
        return $true
    }
    catch {
        Write-Status "Docker not found!" "Error"
        Write-Host "Please install Docker Desktop: https://www.docker.com/products/docker-desktop"
        return $false
    }
}

function Check-DockerRunning {
    try {
        docker ps > $null 2>&1
        Write-Status "Docker daemon is running" "Success"
        return $true
    }
    catch {
        Write-Status "Docker daemon not running!" "Error"
        Write-Host "Please start Docker Desktop and try again."
        return $false
    }
}

function Check-DotEnv {
    if (Test-Path ".env") {
        Write-Status ".env file found" "Success"
        return $true
    }
    
    if (Test-Path ".env.example") {
        Write-Status ".env file not found, creating from .env.example" "Warning"
        Copy-Item ".env.example" ".env"
        Write-Status ".env created successfully" "Success"
        return $true
    }
    
    Write-Status ".env and .env.example not found!" "Error"
    return $false
}

# Main execution
Write-Host ""
Write-Host "============================================================================" -ForegroundColor $Cyan
Write-Host "IC MemTrendDashboard — Docker Setup" -ForegroundColor $Cyan
Write-Host "============================================================================" -ForegroundColor $Cyan
Write-Host ""

# Navigate to script directory
Push-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

try {
    # Check prerequisites
    Write-Host "Checking prerequisites..." -ForegroundColor $Cyan
    Write-Host ""
    
    if (-not (Check-DotEnv)) {
        exit 1
    }
    
    if (-not (Check-Docker)) {
        exit 1
    }
    
    if (-not (Check-DockerRunning)) {
        exit 1
    }
    
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor $Cyan
    Write-Host "Starting Docker Compose..." -ForegroundColor $Cyan
    Write-Host "============================================================================" -ForegroundColor $Cyan
    Write-Host ""
    Write-Host "Services will be available at:" -ForegroundColor $Yellow
    Write-Host "  Frontend:     http://localhost:8510" -ForegroundColor $Cyan
    Write-Host "  Backend API:  http://localhost:18000" -ForegroundColor $Cyan
    Write-Host "  API Docs:     http://localhost:18000/docs" -ForegroundColor $Cyan
    Write-Host "  Database:     localhost:5433 (PostgreSQL)" -ForegroundColor $Cyan
    Write-Host ""
    Write-Host "Logs below. Press Ctrl+C to stop all services." -ForegroundColor $Yellow
    Write-Host ""
    
    # Start Docker Compose
    docker-compose up --build
    
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor $Cyan
    Write-Host "Docker containers stopped." -ForegroundColor $Cyan
    Write-Host "============================================================================" -ForegroundColor $Cyan
    Write-Host ""
    Write-Host "To remove all containers and data:" -ForegroundColor $Yellow
    Write-Host "  docker-compose down -v" -ForegroundColor $Cyan
    Write-Host ""
}
catch {
    Write-Status $_.Exception.Message "Error"
    exit 1
}
finally {
    Pop-Location
}
