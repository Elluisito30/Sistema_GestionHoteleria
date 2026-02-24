@echo off
REM Ejecutar la aplicación Streamlit (Windows)
cd /d "%~dp0.."
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo No se encontró el entorno virtual (venv). Ejecute: python -m venv venv
    pause
    exit /b 1
)
echo Iniciando Sistema de Gestion Hotelera...
streamlit run src\app.py
pause
