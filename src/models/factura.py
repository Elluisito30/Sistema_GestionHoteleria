"""Modelo de facturas"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import date, datetime
from config.database import db


@dataclass
class Factura:
    id: Optional[int] = None
    numero_factura: str = ""
    huesped_id: Optional[int] = None
    reserva_id: Optional[int] = None
    subtotal: float = 0.0
    impuestos: float = 0.0
    total: float = 0.0
    metodo_pago: Optional[str] = None
    estado: str = "pendiente"
    notas: Optional[str] = None

    @classmethod
    def get_by_id(cls, factura_id: int):
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT f.*, h.nombre || ' ' || h.apellido as huesped_nombre
                FROM facturas f
                LEFT JOIN huespedes h ON f.huesped_id = h.id
                WHERE f.id = %s
            """, (factura_id,))
            return cursor.fetchone()

    @classmethod
    def get_by_numero(cls, numero: str):
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM facturas WHERE numero_factura = %s", (numero,))
            return cursor.fetchone()

    @classmethod
    def get_by_reserva(cls, reserva_id: int):
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM facturas WHERE reserva_id = %s", (reserva_id,))
            return cursor.fetchall()

    @classmethod
    def get_por_rango_fechas(cls, fecha_inicio: date, fecha_fin: date) -> List[dict]:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT f.*, h.nombre || ' ' || h.apellido as huesped_nombre
                FROM facturas f
                LEFT JOIN huespedes h ON f.huesped_id = h.id
                WHERE DATE(f.fecha_emision) BETWEEN %s AND %s
                ORDER BY f.fecha_emision DESC
            """, (fecha_inicio, fecha_fin))
            return cursor.fetchall()

    @classmethod
    def generar_numero(cls) -> str:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT COALESCE(
                    (SELECT MAX(CAST(SUBSTRING(numero_factura FROM 5) AS INTEGER)) 
                     FROM facturas WHERE numero_factura LIKE 'FAC%%'),
                    0
                ) + 1 as sig
            """)
            result = cursor.fetchone()
            num = int(result['sig']) if result and result['sig'] else 1
            return f"FAC{num:08d}"
