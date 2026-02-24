# models/reserva.py
from dataclasses import dataclass
from typing import Optional, List
from datetime import date, datetime
from config.database import db

@dataclass
class Reserva:
    id: Optional[int] = None
    codigo_reserva: Optional[str] = None
    huesped_id: int = 0
    fecha_check_in: date = None
    fecha_check_out: date = None
    numero_adultos: int = 1
    numero_ninos: int = 0
    estado: str = 'confirmada'
    habitacion_id: Optional[int] = None
    tarifa_total: float = 0.0
    notas: Optional[str] = None
    
    @classmethod
    def get_by_id(cls, reserva_id: int):
        """Obtiene una reserva por su ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT r.*, 
                       h.nombre as huesped_nombre, 
                       h.apellido as huesped_apellido,
                       h.email as huesped_email,
                       h.telefono as huesped_telefono,
                       hab.numero as habitacion_numero
                FROM reservas r
                JOIN huespedes h ON r.huesped_id = h.id
                LEFT JOIN habitaciones hab ON r.habitacion_id = hab.id
                WHERE r.id = %s
            """, (reserva_id,))
            return cursor.fetchone()
    
    @classmethod
    def get_by_codigo(cls, codigo: str):
        """Obtiene una reserva por su código"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT r.*, 
                       h.nombre as huesped_nombre, 
                       h.apellido as huesped_apellido,
                       h.email as huesped_email,
                       h.telefono as huesped_telefono,
                       hab.numero as habitacion_numero
                FROM reservas r
                JOIN huespedes h ON r.huesped_id = h.id
                LEFT JOIN habitaciones hab ON r.habitacion_id = hab.id
                WHERE r.codigo_reserva = %s
            """, (codigo,))
            return cursor.fetchone()
    
    @classmethod
    def get_by_fechas(cls, fecha_inicio: date, fecha_fin: date):
        """Obtiene reservas en un rango de fechas"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT r.*, h.nombre as huesped_nombre, h.apellido as huesped_apellido,
                       hab.numero as habitacion_numero
                FROM reservas r
                JOIN huespedes h ON r.huesped_id = h.id
                LEFT JOIN habitaciones hab ON r.habitacion_id = hab.id
                WHERE r.fecha_check_in >= %s 
                  AND r.fecha_check_in <= %s
                  AND r.estado NOT IN ('cancelada')
                ORDER BY r.fecha_check_in
            """, (fecha_inicio, fecha_fin))
            return cursor.fetchall()
    
    @classmethod
    def get_activas(cls):
        """
        Retorna reservas activas para recepción.
        Son las que están CONFIRMADAS y cuyo check-in es hoy o futuro.
        """
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT r.*, 
                       h.nombre as huesped_nombre, 
                       h.apellido as huesped_apellido,
                       hab.numero as habitacion_numero
                FROM reservas r
                JOIN huespedes h ON r.huesped_id = h.id
                LEFT JOIN habitaciones hab ON r.habitacion_id = hab.id
                WHERE r.estado = 'confirmada'
                  AND r.fecha_check_out >= CURRENT_DATE
                ORDER BY r.fecha_check_in
            """)
            return cursor.fetchall()
    
    @classmethod
    def get_alojados_ahora(cls):
        """
        Retorna huéspedes actualmente en el hotel.
        Son los que tienen estado COMPLETADA y un alojamiento activo.
        """
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT r.*, 
                       h.nombre as huesped_nombre, 
                       h.apellido as huesped_apellido,
                       hab.numero as habitacion_numero,
                       a.fecha_check_in,
                       a.id as alojamiento_id
                FROM reservas r
                JOIN huespedes h ON r.huesped_id = h.id
                JOIN habitaciones hab ON r.habitacion_id = hab.id
                JOIN alojamientos a ON r.id = a.reserva_id
                WHERE r.estado = 'completada'
                  AND a.fecha_check_out IS NULL
                ORDER BY a.fecha_check_in
            """)
            return cursor.fetchall()
    
    @classmethod
    def get_historial(cls, limite: int = 50):
        """
        Retorna historial de reservas completadas (con check-out)
        """
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT r.*, 
                       h.nombre as huesped_nombre, 
                       h.apellido as huesped_apellido,
                       hab.numero as habitacion_numero,
                       a.fecha_check_in,
                       a.fecha_check_out,
                       f.total as factura_total
                FROM reservas r
                JOIN huespedes h ON r.huesped_id = h.id
                JOIN habitaciones hab ON r.habitacion_id = hab.id
                LEFT JOIN alojamientos a ON r.id = a.reserva_id
                LEFT JOIN facturas f ON r.id = f.reserva_id
                WHERE r.estado = 'completada'
                  AND a.fecha_check_out IS NOT NULL
                ORDER BY a.fecha_check_out DESC
                LIMIT %s
            """, (limite,))
            return cursor.fetchall()
    
    def check_disponibilidad(self) -> bool:
        """Verifica si la habitación está disponible para las fechas"""
        if not self.habitacion_id:
            return False
        
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT verificar_disponibilidad(%s, %s, %s, %s) as disponible
            """, (self.habitacion_id, self.fecha_check_in, 
                  self.fecha_check_out, self.id))
            result = cursor.fetchone()
            return result['disponible'] if result else False
    
    def save(self, usuario_id: int = None):
        """Guarda o actualiza una reserva"""
        with db.get_cursor() as cursor:
            if self.id:  # Update
                cursor.execute("""
                    UPDATE reservas 
                    SET huesped_id = %s, fecha_check_in = %s, fecha_check_out = %s,
                        numero_adultos = %s, numero_ninos = %s, estado = %s,
                        habitacion_id = %s, tarifa_total = %s, notas = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id
                """, (self.huesped_id, self.fecha_check_in, self.fecha_check_out,
                      self.numero_adultos, self.numero_ninos, self.estado,
                      self.habitacion_id, self.tarifa_total, self.notas, self.id))
            else:  # Insert
                cursor.execute("""
                    INSERT INTO reservas 
                    (huesped_id, fecha_check_in, fecha_check_out, numero_adultos,
                     numero_ninos, estado, habitacion_id, tarifa_total, notas, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, codigo_reserva
                """, (self.huesped_id, self.fecha_check_in, self.fecha_check_out,
                      self.numero_adultos, self.numero_ninos, self.estado,
                      self.habitacion_id, self.tarifa_total, self.notas, usuario_id))
            
            result = cursor.fetchone()
            if result:
                self.id = result['id']
                if 'codigo_reserva' in result:
                    self.codigo_reserva = result['codigo_reserva']
            return self.id
    
    def cancelar(self, motivo: str = None, usuario_id: int = None):
        """Cancela una reserva"""
        if not self.id:
            return False
        with db.get_cursor() as cursor:
            # Guardar estado anterior
            cursor.execute("""
                SELECT estado FROM reservas WHERE id = %s
            """, (self.id,))
            row = cursor.fetchone()
            if not row:
                return False
            estado_anterior = row['estado']
            
            # Actualizar reserva
            cursor.execute("""
                UPDATE reservas 
                SET estado = 'cancelada', 
                    fecha_cancelacion = CURRENT_TIMESTAMP,
                    motivo_cancelacion = %s, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id
            """, (motivo, self.id))
            
            # Registrar en historial
            cursor.execute("""
                INSERT INTO historial_estados_reserva 
                (reserva_id, estado_anterior, estado_nuevo, usuario_id, motivo)
                VALUES (%s, %s, 'cancelada', %s, %s)
            """, (self.id, estado_anterior, usuario_id, motivo))
            
            return cursor.fetchone() is not None