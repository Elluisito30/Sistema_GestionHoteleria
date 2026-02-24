import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

# Evitar UnicodeDecodeError al conectar: el servidor puede enviar datos que no son UTF-8 válido.
# Latin1 acepta cualquier byte; forzamos para todas las conexiones de esta app.
os.environ['PGCLIENTENCODING'] = 'LATIN1'

class DatabaseConnection:
    def __init__(self):
        self.connection_params = {
            'host': settings.DB_HOST,
            'port': settings.DB_PORT,
            'database': settings.DB_NAME,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD
        }

    @contextmanager
    def get_connection_auth(self):
        """Conexión para autenticación (usa PGCLIENTENCODING=LATIN1 del módulo)."""
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except Exception as e:
            logger.error(f"Database connection error (auth): {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
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
        """Cursor para consultas de autenticación (evita error de encoding del hash)."""
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

db = DatabaseConnection()