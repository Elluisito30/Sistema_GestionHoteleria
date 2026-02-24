# test_db.py
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir))

# Ahora importamos desde src
from src.config.database import db
from src.config.settings import settings
import logging

# Configurar logging para ver resultados
logging.basicConfig(level=logging.INFO)

print("="*60)
print("🔍 VERIFICACIÓN DE CONEXIÓN A BASE DE DATOS")
print("="*60)
print(f"📊 Entorno: {settings.APP_ENV}")
print(f"🌐 Host: {settings.DB_HOST}")
print(f"🗄️  BD: {settings.DB_NAME}")
print(f"👤 Usuario: {settings.DB_USER}")
print(f"🔒 SSL: {'require' if settings.is_production else 'disabled'}")
print("="*60)

# Probar conexión
if db.test_connection():
    print("\n✅ CONEXIÓN EXITOSA!")
    
    # Obtener información de la BD
    info = db.get_db_info()
    if info:
        print(f"\n📋 Información de la BD:")
        print(f"   - Base de datos: {info['database']}")
        print(f"   - Usuario: {info['user']}")
        print(f"   - Versión: {info['version'][:50]}...")
else:
    print("\n❌ ERROR DE CONEXIÓN")
    print("\n🔧 Posibles soluciones:")
    print("   1. Verifica que PostgreSQL esté corriendo")
    print("   2. Verifica tus credenciales en .env")
    print("   3. Ejecuta: pg_isready -U postgres")
    
print("="*60)