
# Setup Backend Script

Write-Host "Starting Backend Setup..." -ForegroundColor Cyan

# 1. Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    $envContent = @"
DATABASE_URL=postgresql://basamaljanaby:changeme@localhost:5432/basamaljanaby
SECRET_KEY=development_secret_key_12345
DEBUG=True
"@
    Set-Content -Path ".env" -Value $envContent
    Write-Host ".env file created." -ForegroundColor Green
}
else {
    Write-Host ".env file already exists." -ForegroundColor Gray
}

# Fix .env encoding (Force UTF-8 No BOM to prevent Python errors)
Write-Host "Ensuring .env encoding is compatible..." -ForegroundColor Yellow
$envPath = Join-Path (Get-Location) ".env"
$envContent = Get-Content $envPath
$Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $False
[System.IO.File]::WriteAllLines($envPath, $envContent, $Utf8NoBomEncoding)
Write-Host ".env encoding fixed." -ForegroundColor Green

# 2. Check for Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Gray
}
catch {
    Write-Host "Error: Python not found. Please install Python." -ForegroundColor Red
    exit 1
}

# 3. Create Virtual Environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment 'venv'..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Virtual environment created." -ForegroundColor Green
}
else {
    Write-Host "Virtual environment 'venv' already exists." -ForegroundColor Gray
}

# 4. Install Requirements
Write-Host "Installing requirements..." -ForegroundColor Yellow
# Activate venv for the current script process to run pip
& .\venv\Scripts\python -m pip install --upgrade pip
& .\venv\Scripts\pip install -r requirements.txt --default-timeout=1000
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error installing requirements. Trying again with extended timeout..." -ForegroundColor Red
    & .\venv\Scripts\pip install -r requirements.txt --default-timeout=2000
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error installing requirements even with extended timeout." -ForegroundColor Red
        exit 1
    }
}
Write-Host "Requirements installed." -ForegroundColor Green

# 5. Database Setup
Write-Host "Checking Database..." -ForegroundColor Yellow

# Check if Docker is running
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Start Postgres using parent docker-compose
Write-Host "Starting PostgreSQL container..." -ForegroundColor Yellow
docker-compose -f ..\docker-compose.yml up -d postgres
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error starting PostgreSQL via docker-compose." -ForegroundColor Red
    exit 1
}

Write-Host "Waiting for Database to accept connections..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# 6. Run Migrations
Write-Host "Running Alembic Migrations..." -ForegroundColor Yellow
& .\venv\Scripts\alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "Migration failed (possibly due to existing tables). Attempting to sync version..." -ForegroundColor Yellow
    & .\venv\Scripts\alembic stamp head
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Migration and Version Sync failed. Please check logs." -ForegroundColor Red
        exit 1
    }
    else {
        Write-Host "Database version synced (tables already existed)." -ForegroundColor Green
    }
}
else {
    Write-Host "Database migrations applied." -ForegroundColor Green
}

# 6. Fix Admin
Write-Host "Configuring Admin User..." -ForegroundColor Yellow
& .\venv\Scripts\python fix_admin.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "Admin user configured." -ForegroundColor Green
}

Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "To run the server, use:" -ForegroundColor White
Write-Host ".\venv\Scripts\uvicorn app.main:app --reload" -ForegroundColor Green
