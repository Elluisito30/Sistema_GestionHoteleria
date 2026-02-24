# Script para inicializar la base de datos PostgreSQL
# Uso: .\scripts\init_db.ps1
# Requiere: psql en PATH o ruta completa a psql

$DB_NAME = if ($env:DB_NAME) { $env:DB_NAME } else { "hotel_db" }
$DB_USER = if ($env:DB_USER) { $env:DB_USER } else { "postgres" }
$DB_HOST = if ($env:DB_HOST) { $env:DB_HOST } else { "localhost" }
$DB_PORT = if ($env:DB_PORT) { $env:DB_PORT } else { "5432" }

$ScriptDir = Split-Path -Parent $PSScriptRoot
$DbDir = Join-Path $ScriptDir "database"

Write-Host "=== Inicializando base de datos $DB_NAME ===" -ForegroundColor Cyan
Write-Host "Host: $DB_HOST`:$DB_PORT | Usuario: $DB_USER" -ForegroundColor Gray

# Crear base de datos si no existe
$env:PGPASSWORD = $env:DB_PASSWORD
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | ForEach-Object {
    if ($_ -match "1") {
        Write-Host "Base de datos $DB_NAME ya existe" -ForegroundColor Yellow
    } else {
        Write-Host "Creando base de datos $DB_NAME..." -ForegroundColor Green
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"
    }
}

# Ejecutar scripts en orden
$scripts = @("schema.sql", "seeds.sql", "indexes.sql", "views.sql")
foreach ($script in $scripts) {
    $path = Join-Path $DbDir $script
    if (Test-Path $path) {
        Write-Host "Ejecutando $script..." -ForegroundColor Green
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f $path 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error ejecutando $script" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host "`n=== Base de datos inicializada correctamente ===" -ForegroundColor Green
