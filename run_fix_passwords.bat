@echo off
echo ============================================
echo   Sistema Hotelero - Actualizar Contraseñas
echo ============================================
echo.

cd /d "%~dp0"

REM ✅ Usar UTF-8 en lugar de LATIN1 (evita UnicodeDecodeError)
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

REM ✅ Ejecutar con el flag --generar para las contraseñas correctas
echo Ejecutando con las siguientes credenciales:
echo   - admin / adminSistema
echo   - gerente / gerenteSistema
echo   - recepcion1 / recepcionista1Sistema
echo.

python fix_passwords_db.py --generar

echo.
if errorlevel 1 (
    echo ❌ Error al ejecutar el script
    pause
    exit /b 1
) else (
    echo.
    echo ============================================
    echo   ✅ Contraseñas actualizadas correctamente
    echo ============================================
    echo.
    echo Ahora reinicia tu servidor Python y prueba login
    echo.
    pause
)
