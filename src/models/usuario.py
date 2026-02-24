"""Modelo de usuarios del sistema"""
from dataclasses import dataclass
from typing import Optional, List
from config.database import db


@dataclass
class Usuario:
    id: Optional[int] = None
    username: str = ""
    nombre_completo: str = ""
    email: str = ""
    rol: str = "recepcionista"
    activo: bool = True

    @classmethod
    def get_by_id(cls, usuario_id: int):
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT id, username, nombre_completo, email, rol, activo FROM usuarios WHERE id = %s",
                (usuario_id,)
            )
            return cursor.fetchone()

    @classmethod
    def get_by_username(cls, username: str):
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM usuarios WHERE username = %s AND activo = true",
                (username,)
            )
            return cursor.fetchone()

    @classmethod
    def get_all(cls, solo_activos: bool = True) -> List[dict]:
        with db.get_cursor() as cursor:
            query = "SELECT id, username, nombre_completo, email, rol, activo, ultimo_acceso FROM usuarios"
            if solo_activos:
                query += " WHERE activo = true"
            query += " ORDER BY nombre_completo"
            cursor.execute(query)
            return cursor.fetchall()
