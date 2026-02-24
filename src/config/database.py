# src/config/database.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import logging
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importaciones absolutas
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

# Ahora podemos importar desde src.config
from src.config.settings import settings

logger = logging.getLogger(__name__)

# Forzar encoding Latin1 para evitar UnicodeDecodeError con contraseñas
os.environ['PGCLIENTENCODING'] = 'LATIN1'

class DatabaseConnection:
    def __init__(self):
        # Parámetros base de conexión
        self.base_params = {
            'host': settings.DB_HOST,
            'port': settings.DB_PORT,
            'database': settings.DB_NAME,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD,
        }
        
        # Detectar si estamos en producción (Neon)
        self.is_production = settings.is_production or 'neon.tech' in settings.DB_HOST
        
        # Configuración de SSL para Neon
        if self.is_production:
            logger.info("🔒 Modo producción detectado - Activando SSL")
            self.base_params['sslmode'] = 'require'
        else:
            logger.info("🖥️ Modo local detectado")
        
        # Timeouts y configuraciones adicionales
        self.base_params['connect_timeout'] = 10
        self.base_params['keepalives_idle'] = 30
        self.base_params['keepalives_interval'] = 10
        self.base_params['keepalives_count'] = 5

    def _get_connection_params(self, for_auth=False):
        """Obtiene parámetros de conexión"""
        params = self.base_params.copy()
        if for_auth:
            logger.debug("Usando configuración para autenticación")
        return params

    @contextmanager
    def get_connection_auth(self):
        """Conexión para autenticación (usa Latin1 para hashes)"""
        conn = None
        params = self._get_connection_params(for_auth=True)
        
        try:
            logger.debug(f"Conectando a BD (auth): {params['host']}/{params['database']}")
            conn = psycopg2.connect(**params)
            yield conn
        except psycopg2.OperationalError as e:
            logger.error(f"Error operacional de BD (auth): {e}")
            self._show_connection_help(e)
            raise
        except Exception as e:
            logger.error(f"Error de conexión a BD (auth): {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_connection(self):
        """Conexión normal para operaciones generales"""
        conn = None
        params = self._get_connection_params(for_auth=False)
        
        try:
            logger.debug(f"Conectando a BD: {params['host']}/{params['database']}")
            conn = psycopg2.connect(**params)
            yield conn
        except psycopg2.OperationalError as e:
            logger.error(f"Error operacional de BD: {e}")
            self._show_connection_help(e)
            raise
        except Exception as e:
            logger.error(f"Error de conexión a BD: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """Obtiene un cursor para operaciones normales"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()

    @contextmanager
    def get_cursor_auth(self, cursor_factory=RealDictCursor):
        """Obtiene un cursor específico para autenticación (Latin1)"""
        with self.get_connection_auth() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()
    
    def test_connection(self):
        """Prueba la conexión a la base de datos"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result:
                    logger.info("✅ Conexión a BD exitosa")
                    return True
        except Exception as e:
            logger.error(f"❌ Error probando conexión: {e}")
            return False
        return False
    
    def get_db_info(self):
        """Obtiene información de la base de datos"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        current_database() as database,
                        current_user as user,
                        version() as version
                """)
                info = cursor.fetchone()
                return info
        except Exception as e:
            logger.error(f"Error obteniendo info de BD: {e}")
            return None
    
    def _show_connection_help(self, error):
        """Muestra ayuda para errores de conexión comunes"""
        error_str = str(error).lower()
        
        if "password" in error_str or "authentication" in error_str:
            logger.error("🔐 Error de autenticación. Verifica tu usuario y contraseña.")
        elif "timeout" in error_str:
            logger.error("⏱️ Timeout de conexión. Verifica que el host sea accesible.")
        elif "refused" in error_str:
            logger.error("🚫 Conexión rechazada. Verifica que PostgreSQL esté corriendo.")
        elif "ssl" in error_str and self.is_production:
            logger.error("🔒 Error SSL. Verifica que Neon requiera SSL (sslmode=require).")
        
        if self.is_production:
            logger.info("💡 Sugerencia: En producción (Neon), verifica que los secrets estén configurados correctamente.")
        else:
            logger.info("💡 Sugerencia: En local, verifica que PostgreSQL esté corriendo en localhost:5432")

# Instancia global
db = DatabaseConnection()