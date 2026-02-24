"""
Script para corregir los hashes de contraseña en la base de datos.

POR QUÉ FALLA SI USASTE generar_hashes.py Y PEGASTE LOS UPDATE EN POSTGRESQL:
  Si generaste hashes con generar_hashes.py y copiaste/pegaste los UPDATE en pgAdmin/psql,
  el hash puede haberse guardado con encoding incorrecto. La columna password_hash queda
  con bytes que no son UTF-8 válidos → al leer, la app lanza UnicodeDecodeError.

SOLUCIÓN: Escribir el hash desde Python con este script (conexión + parámetros).

Uso desde la raíz del proyecto:
  python fix_passwords_db.py              → admin123, gerente123, recepcion123
  python fix_passwords_db.py --generar    → adminSistema, gerenteSistema, recepcionista1Sistema

Requisitos: .env configurado (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
"""
import os
import sys

# Forzar Latin1 antes de conectar a PostgreSQL
os.environ['PGCLIENTENCODING'] = 'LATIN1'

# Cargar .env con Latin1 siempre (nunca UTF-8 aquí, evita el error de decode)
def _load_env():
    base = os.path.dirname(os.path.abspath(__file__))
    for name in ('.env', '.env.local'):
        path = os.path.join(base, name)
        if os.path.isfile(path):
            with open(path, encoding='latin1') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, _, v = line.partition('=')
                        v = v.strip().strip('"').strip("'")
                        os.environ.setdefault(k.strip(), v)
            break

_load_env()

def _get_port():
    try:
        return int(os.getenv('DB_PORT', '5432'))
    except ValueError:
        return 5432

import psycopg2

# 3 usuarios con 3 contraseñas diferentes (para modo por defecto)
CREDENCIALES_DEMO = {
    'admin': 'admin123',
    'gerente': 'gerente123',
    'recepcion1': 'recepcion123',
}

# Mismas credenciales que generar_hashes.py (para opción --generar)
CREDENCIALES_GENERAR = {
    'admin': 'adminSistema',
    'gerente': 'gerenteSistema',
    'recepcionista1': 'recepcionista1Sistema',
}


def generar_hashes_desde_python(credenciales_dict):
    """Genera hashes con bcrypt y los devuelve como str (ASCII) para guardar en BD."""
    import bcrypt
    result = {}
    for usuario, password in credenciales_dict.items():
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
        result[usuario] = hashed.decode('utf-8')
    return result


def main():
    usar_generar = '--generar' in sys.argv

    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=_get_port(),
            database=os.getenv('DB_NAME', 'hotel_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
        )
        with conn.cursor() as cur:
            if usar_generar:
                credenciales = CREDENCIALES_GENERAR
            else:
                credenciales = CREDENCIALES_DEMO
            # Escribir en la BD un hash distinto por usuario
            hashes = generar_hashes_desde_python(credenciales)
            for usuario, hash_str in hashes.items():
                cur.execute(
                    "UPDATE usuarios SET password_hash = %s WHERE username = %s",
                    (hash_str, usuario),
                )
            conn.commit()
            print("OK: Se actualizaron 3 usuario(s) con contraseñas diferentes:")
            for u, p in credenciales.items():
                print(f"   {u} → contraseña: {p}")
        print("Vuelve a intentar iniciar sesión en la app.")
    except Exception as e:
        # Mostrar el traceback completo para saber exactamente dónde se produce el error
        import traceback
        print("Error al ejecutar fix_passwords_db.py:", file=sys.stderr)
        traceback.print_exc()
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    main()
