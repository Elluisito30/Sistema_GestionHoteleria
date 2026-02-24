import os

# Cargar .env: intentar UTF-8; si falla (ej. contraseña con acentos guardada en Latin1), usar Latin1
def _load_dotenv_safe():
    from pathlib import Path
    base = Path(__file__).resolve().parent.parent.parent  # raíz del proyecto
    for name in ('.env', '.env.local'):
        path = base / name
        if path.is_file():
            try:
                content = path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                content = path.read_text(encoding='latin1')
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, _, v = line.partition('=')
                    v = v.strip().strip('"').strip("'")
                    os.environ.setdefault(k.strip(), v)
            return
    try:
        from dotenv import load_dotenv
        load_dotenv(base / '.env', encoding='utf-8')
    except (UnicodeDecodeError, Exception):
        pass

_load_dotenv_safe()

def _get_port():
    try:
        return int(os.getenv('DB_PORT', '5432'))
    except ValueError:
        return 5432

class Settings:
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = _get_port()
    DB_NAME = os.getenv('DB_NAME', 'hotel_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    
    # App
    APP_NAME = "Sistema de Gestión Hotelera"
    APP_VERSION = "Login System"
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Credenciales de demostración (3 usuarios, 3 contraseñas diferentes)
    DEMO_CREDENTIALS = [
        {"usuario": "admin", "contraseña": "admin123", "rol": "Administrador"},
        {"usuario": "gerente", "contraseña": "gerente123", "rol": "Gerente"},
        {"usuario": "recepcion1", "contraseña": "recepcion123", "rol": "Recepcionista"},
    ]
    
    # Paths (relativos a la raíz del proyecto)
    LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
    REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")
    
    @property
    def database_url(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()