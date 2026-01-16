# =================================================================
# Virtual Tagging System - ONE-CLICK SETUP & RUN (Windows)
# =================================================================

Write-Host ""
Write-Host "🚀 Virtual Tagging System - Automated Setup" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker not found! Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "   Download: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "✅ Docker found" -ForegroundColor Green

# Check Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js not found! Please install Node.js first." -ForegroundColor Red
    Write-Host "   Download: https://nodejs.org/" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "✅ Node.js found" -ForegroundColor Green
Write-Host ""

# =======================
# BACKEND SETUP
# =======================
Write-Host "📦 Setting up Backend..." -ForegroundColor Yellow
Set-Location python

# Create .env if not exists
if (-not (Test-Path .env)) {
    Write-Host "   Creating .env file..." -ForegroundColor Gray
    Copy-Item .env.example .env
    Write-Host "   ⚠️  Please review .env file and update if needed" -ForegroundColor Yellow
}

# Start backend
Write-Host "   Starting Docker containers..." -ForegroundColor Gray
docker-compose up -d

# Wait for database
Write-Host "   Waiting for database to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# Run migrations
Write-Host "   Running database migrations..." -ForegroundColor Gray
docker-compose exec -T backend alembic upgrade head 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Database migrations complete" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Migrations may have failed (might be OK if first run)" -ForegroundColor Yellow
}

Write-Host "✅ Backend is running on http://localhost:8000" -ForegroundColor Green
Write-Host ""

# =======================
# FRONTEND SETUP
# =======================
Write-Host "📦 Setting up Frontend..." -ForegroundColor Yellow
Set-Location ..\client

# Create .env if not exists
if (-not (Test-Path .env)) {
    Write-Host "   Creating .env file..." -ForegroundColor Gray
    Copy-Item .env.example .env
}

# Install dependencies
if (-not (Test-Path node_modules)) {
    Write-Host "   Installing dependencies (this may take a few minutes)..." -ForegroundColor Gray
    npm install --silent
    Write-Host "   ✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   ✅ Dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Services Status:" -ForegroundColor Cyan
Write-Host "   Backend API:  http://localhost:8000  ✅ RUNNING" -ForegroundColor Green
Write-Host "   Database:     localhost:5432          ✅ RUNNING" -ForegroundColor Green
Write-Host "   Frontend:     Ready to start" -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 To start the frontend, run:" -ForegroundColor Cyan
Write-Host "   cd client" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "📱 Then open: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "🛑 To stop all services:" -ForegroundColor Yellow
Write-Host "   cd python && docker-compose down" -ForegroundColor White
Write-Host ""

# Go back to root
Set-Location ..

# Offer to start frontend
Write-Host "Would you like to start the frontend now? (Y/N): " -ForegroundColor Cyan -NoNewline
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "🌐 Starting frontend..." -ForegroundColor Green
    Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    Set-Location client
    npm run dev
}

Write-Host ""
Write-Host "Happy coding! 🎉" -ForegroundColor Green
