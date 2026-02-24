from dataclasses import dataclass
from typing import Optional
from datetime import date
from config.database import db

@dataclass
class Huesped:
    id: Optional[int] = None
    uuid: Optional[str] = None
    tipo_documento: str = ''
    numero_documento: str = ''
    nombre: str = ''
    apellido: str = ''
    fecha_nacimiento: Optional[date] = None
    nacionalidad: str = 'Peruana'
    email: Optional[str] = None
    telefono: str = ''
    pais_origen: str = 'Perú'          # Cambiamos nombre para claridad
    ciudad_origen: str = ''            # Ciudad de origen
    direccion: Optional[str] = None
    distrito: Optional[str] = None      # Nuevo campo
    codigo_postal: Optional[str] = None
    preferencias: Optional[str] = None
    es_vip: bool = False
    
    @classmethod
    def get_by_id(cls, id: int):
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM huespedes WHERE id = %s", (id,))
            return cursor.fetchone()
    
    @classmethod
    def get_by_documento(cls, numero_documento: str):
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM huespedes WHERE numero_documento = %s", (numero_documento,))
            return cursor.fetchone()
    
    @classmethod
    def buscar(cls, termino: str):
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM huespedes 
                WHERE nombre ILIKE %s 
                   OR apellido ILIKE %s 
                   OR numero_documento ILIKE %s
                   OR email ILIKE %s
                ORDER BY nombre, apellido
                LIMIT 20
            """, (f'%{termino}%', f'%{termino}%', f'%{termino}%', f'%{termino}%'))
            return cursor.fetchall()
    
    def save(self):
        with db.get_cursor() as cursor:
            if self.id:
                cursor.execute("""
                    UPDATE huespedes
                    SET tipo_documento = %s, numero_documento = %s, nombre = %s,
                        apellido = %s, fecha_nacimiento = %s, nacionalidad = %s,
                        email = %s, telefono = %s, pais = %s, ciudad = %s,
                        direccion = %s, distrito = %s, codigo_postal = %s,
                        preferencias = %s, es_vip = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id
                """, (self.tipo_documento, self.numero_documento, self.nombre,
                      self.apellido, self.fecha_nacimiento, self.nacionalidad,
                      self.email, self.telefono, self.pais_origen, self.ciudad_origen,
                      self.direccion, self.distrito, self.codigo_postal,
                      self.preferencias, self.es_vip, self.id))
            else:
                cursor.execute("""
                    INSERT INTO huespedes
                    (tipo_documento, numero_documento, nombre, apellido,
                     fecha_nacimiento, nacionalidad, email, telefono,
                     pais, ciudad, direccion, distrito, codigo_postal, preferencias, es_vip)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (self.tipo_documento, self.numero_documento, self.nombre,
                      self.apellido, self.fecha_nacimiento, self.nacionalidad,
                      self.email, self.telefono, self.pais_origen, self.ciudad_origen,
                      self.direccion, self.distrito, self.codigo_postal,
                      self.preferencias, self.es_vip))
            result = cursor.fetchone()
            if result:
                self.id = result['id']
            return self.id