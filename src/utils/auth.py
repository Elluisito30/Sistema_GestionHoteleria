import bcrypt
from config.database import db
from utils.logger import logger

class Auth:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed) -> bool:
        """Verify a password against its hash. Acepta str (leído con Latin1) o bytes."""
        try:
            # Validar que hashed no sea None o vacío
            if not hashed:
                logger.error("Hash de contraseña vacío o None")
                return False
            
            password_bytes = password.encode('utf-8')
            # El hash desde BD puede venir como str (conexión Latin1) o bytes; nunca decodificar como UTF-8
            if isinstance(hashed, bytes):
                hashed_bytes = hashed
            else:
                # str: convertir a bytes con Latin1 (1 byte por carácter, evita UnicodeDecodeError)
                hashed_bytes = hashed.encode('latin1')
            
            return bcrypt.checkpw(password_bytes, hashed_bytes)
            
        except bcrypt.exceptions.InvalidSalt as e:
            logger.error(f"Hash inválido (salt): {str(e)}")
            return False
        except bcrypt.exceptions.InvalidHash as e:
            logger.error(f"Hash inválido: {str(e)}")
            return False
        except UnicodeEncodeError as e:
            logger.error(f"Error de encoding: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado en verify_password: {type(e).__name__} - {str(e)}")
            return False
    
    @staticmethod
    def authenticate(username: str, password: str):
        """Authenticate a user"""
        try:
            logger.info(f"Intento de autenticación para usuario: {username}")
            
            # Usar conexión con Latin1 para leer password_hash sin UnicodeDecodeError
            with db.get_cursor_auth() as cursor:
                cursor.execute("""
                    SELECT id, username, nombre_completo, email, rol, password_hash
                    FROM usuarios
                    WHERE username = %s AND activo = true
                """, (username,))
                
                user = cursor.fetchone()
                
                if user:
                    logger.debug(f"Usuario encontrado: {user['username']}, rol: {user['rol']}")
                else:
                    logger.warning(f"No se encontró usuario: {username}")
                    return False, "Usuario o contraseña incorrectos"
                
                # Verificar contraseña
                if user and Auth.verify_password(password, user['password_hash']):
                    # Update last access
                    cursor.execute("""
                        UPDATE usuarios 
                        SET ultimo_acceso = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (user['id'],))
                    
                    # Remove password hash from result
                    user_dict = {
                        'id': user['id'],
                        'username': user['username'],
                        'nombre_completo': user['nombre_completo'],
                        'email': user['email'],
                        'rol': user['rol']
                    }
                    
                    logger.info(f"✅ Usuario autenticado exitosamente: {username}")
                    return True, user_dict
                else:
                    logger.warning(f"❌ Contraseña incorrecta para usuario: {username}")
                    return False, "Usuario o contraseña incorrectos"
                    
        except Exception as e:
            logger.error(f"❌ Error en autenticación: {type(e).__name__} - {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False, "Error en el sistema de autenticación"
    
    @staticmethod
    def logout():
        """Logout user - handled by session state"""
        logger.info("Usuario cerró sesión")
        return True
    
    @staticmethod
    def check_role(required_role: str, user_role: str) -> bool:
        """Check if user has required role"""
        role_hierarchy = {
            'admin': 3,
            'gerente': 2,
            'recepcionista': 1
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)