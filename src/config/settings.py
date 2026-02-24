# src/config/settings.py
import os
from pathlib import Path
import logging

# =============================================================================
# CARGA DE VARIABLES DE ENTORNO (robusta a encoding)
# =============================================================================
def _load_dotenv_safe():
    """
    Carga variables de entorno desde .env o .env.local
    Soporta UTF-8 y Latin1 (para contraseñas con acentos)
    """
    base = Path(__file__).resolve().parent.parent.parent  # raíz del proyecto
    
    for name in ('.env', '.env.local'):
        path = base / name
        if path.is_file():
            try:
                # Intentar leer como UTF-8 primero
                content = path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Si falla, usar Latin1
                content = path.read_text(encoding='latin1')
            
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, _, v = line.partition('=')
                    v = v.strip().strip('"').strip("'")
                    os.environ.setdefault(k.strip(), v)
            return
    
    # Fallback: intentar con python-dotenv si existe
    try:
        from dotenv import load_dotenv
        env_file = base / '.env'
        if env_file.exists():
            try:
                load_dotenv(env_file, encoding='utf-8')
            except UnicodeDecodeError:
                load_dotenv(env_file, encoding='latin1')
    except ImportError:
        # python-dotenv no está instalado
        pass

# Cargar variables de entorno
_load_dotenv_safe()

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================
def _get_port():
    """Obtiene el puerto como entero"""
    try:
        return int(os.getenv('DB_PORT', '5432'))
    except ValueError:
        return 5432

def _get_bool(var_name, default=False):
    """Convierte variable de entorno a booleano"""
    value = os.getenv(var_name, '').lower()
    if value in ('true', '1', 'yes', 'on'):
        return True
    if value in ('false', '0', 'no', 'off'):
        return False
    return default

# =============================================================================
# CLASE PRINCIPAL DE CONFIGURACIÓN
# =============================================================================
class Settings:
    def __init__(self):
        # ===== DETECCIÓN DE ENTORNO =====
        # Intentar cargar desde Streamlit secrets (solo si estamos en Streamlit Cloud)
        self._load_from_streamlit_safe()
        
        # ===== DATABASE =====
        self.DB_HOST = os.getenv('DB_HOST', 'localhost')
        self.DB_PORT = _get_port()
        self.DB_NAME = os.getenv('DB_NAME', 'hotel_db')
        self.DB_USER = os.getenv('DB_USER', 'postgres')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
        
        # ===== APP =====
        self.APP_NAME = os.getenv('APP_NAME', 'Sistema de Gestión Hotelera')
        self.APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
        
        # Entorno y debug
        self.APP_ENV = os.getenv('APP_ENV', 'development')
        self.DEBUG = _get_bool('DEBUG', self.APP_ENV == 'development')
        
        # ===== CREDENCIALES DE DEMO =====
        self.DEMO_CREDENTIALS = [
            {"usuario": "admin", "contraseña": "admin123", "rol": "Administrador"},
            {"usuario": "gerente", "contraseña": "gerente123", "rol": "Gerente"},
            {"usuario": "recepcion1", "contraseña": "recepcion123", "rol": "Recepcionista"},
        ]
        
        # ===== PATHS =====
        self.BASE_DIR = Path(__file__).resolve().parent.parent.parent
        self.LOGS_DIR = self.BASE_DIR / "logs"
        self.REPORTS_DIR = self.BASE_DIR / "reports"
        
        # Crear directorios si no existen
        self.LOGS_DIR.mkdir(exist_ok=True)
        self.REPORTS_DIR.mkdir(exist_ok=True)
    
    def _load_from_streamlit_safe(self):
        """Intenta cargar configuración desde Streamlit secrets sin causar error"""
        try:
            import streamlit as st
            # Verificar si estamos en Streamlit Cloud (los secrets existen)
            try:
                # Intentar acceder a secrets de manera segura
                if hasattr(st, 'secrets') and st.secrets:
                    for key in ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 
                                'APP_ENV', 'DEBUG', 'SECRET_KEY']:
                        if key in st.secrets:
                            os.environ[key] = st.secrets[key]
            except Exception as e:
                # Si hay cualquier error con secrets, simplemente ignoramos
                # (esto pasa en desarrollo local)
                pass
        except ImportError:
            # streamlit no está instalado o no podemos importarlo
            pass
        except Exception:
            # Cualquier otro error, ignoramos
            pass
    
    @property
    def database_url(self):
        """URL completa para SQLAlchemy"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def connection_params(self):
        """Parámetros para psycopg2"""
        params = {
            'host': self.DB_HOST,
            'port': self.DB_PORT,
            'database': self.DB_NAME,
            'user': self.DB_USER,
            'password': self.DB_PASSWORD,
        }
        
        # Agregar SSL si es producción o Neon
        if self.is_production or 'neon.tech' in self.DB_HOST:
            params['sslmode'] = 'require'
        
        return params
    
    @property
    def is_production(self):
        """Determina si estamos en producción"""
        return self.APP_ENV == 'production' or 'neon.tech' in self.DB_HOST
    
    def get_credential(self, username):
        """Obtiene credenciales de demo por nombre de usuario"""
        for cred in self.DEMO_CREDENTIALS:
            if cred["usuario"] == username:
                return cred
        return None
    
    def __repr__(self):
        """Representación de la configuración (útil para debugging)"""
        return f"""<Settings
    ENV: {self.APP_ENV}
    DEBUG: {self.DEBUG}
    DB: {self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}
    SSL: {'require' if self.is_production else 'disabled'}
>"""

# Instancia global
settings = Settings()

# Configurar logging básico
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOGS_DIR / 'hotel.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Mostrar configuración al iniciar (solo en debug)
if settings.DEBUG:
    print(f"🔧 Configuración cargada: {settings}")