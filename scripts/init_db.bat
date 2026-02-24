@echo off
REM Script para inicializar la base de datos PostgreSQL (Windows)
REM Uso: scripts\init_db.bat

cd /d "%~dp0.."

set DB_NAME=%DB_NAME%
if "%DB_NAME%"=="" set DB_NAME=hotel_db
set DB_USER=%DB_USER%
if "%DB_USER%"=="" set DB_USER=postgres
set DB_HOST=%DB_HOST%
if "%DB_HOST%"=="" set DB_HOST=localhost
set DB_PORT=%DB_PORT%
if "%DB_PORT%"=="" set DB_PORT=5432

echo === Inicializando base de datos %DB_NAME% ===

REM Crear BD si no existe
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d postgres -c "SELECT 1 FROM pg_database WHERE datname='%DB_NAME%'" | findstr "1" >nul 2>&1
if errorlevel 1 (
    echo Creando base de datos %DB_NAME%...
    psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d postgres -c "CREATE DATABASE %DB_NAME%;"
)

REM Ejecutar scripts
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f database\schema.sql
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f database\seeds.sql
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f database\indexes.sql
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f database\views.sql

echo.
echo === Base de datos inicializada ===
