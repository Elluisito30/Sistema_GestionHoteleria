"""Controlador de reportes - agrupa consultas para reportes"""
from typing import List, Dict, Optional
from datetime import date
from config.database import db
from utils.logger import logger


class ReporteController:

    @staticmethod
    def get_ocupacion_periodo(fecha_inicio: date, fecha_fin: date) -> List[Dict]:
        """Obtiene datos de ocupación diaria para un período"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    WITH fechas AS (
                        SELECT generate_series(%s::date, %s::date, '1 day'::interval)::date as fecha
                    )
                    SELECT 
                        f.fecha,
                        COUNT(DISTINCT CASE 
                            WHEN r.fecha_check_in <= f.fecha 
                            AND r.fecha_check_out > f.fecha
                            AND r.estado IN ('confirmada', 'completada')
                            THEN r.habitacion_id 
                        END) as habitaciones_ocupadas,
                        COUNT(DISTINCT r.id) as reservas_activas,
                        COALESCE(SUM(CASE 
                            WHEN r.fecha_check_in <= f.fecha 
                            AND r.fecha_check_out > f.fecha
                            AND r.estado IN ('confirmada', 'completada')
                            THEN 1 
                        END), 0) as huespedes
                    FROM fechas f
                    LEFT JOIN reservas r ON 
                        r.fecha_check_in <= f.fecha 
                        AND r.fecha_check_out > f.fecha
                    GROUP BY f.fecha
                    ORDER BY f.fecha
                """, (fecha_inicio, fecha_fin))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error en reporte ocupación: {str(e)}")
            return []

    @staticmethod
    def get_ingresos_periodo(fecha_inicio: date, fecha_fin: date) -> List[Dict]:
        """Obtiene ingresos por día para un período"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        DATE(fecha_emision) as fecha,
                        COUNT(DISTINCT id) as total_facturas,
                        SUM(total) as ingresos,
                        SUM(CASE WHEN metodo_pago = 'efectivo' THEN total ELSE 0 END) as efectivo,
                        SUM(CASE WHEN metodo_pago = 'tarjeta' THEN total ELSE 0 END) as tarjeta,
                        SUM(CASE WHEN metodo_pago = 'transferencia' THEN total ELSE 0 END) as transferencia
                    FROM facturas
                    WHERE DATE(fecha_emision) BETWEEN %s AND %s
                    AND estado = 'pagada'
                    GROUP BY DATE(fecha_emision)
                    ORDER BY fecha
                """, (fecha_inicio, fecha_fin))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error en reporte ingresos: {str(e)}")
            return []

    @staticmethod
    def get_kpis_periodo(fecha_inicio: date, fecha_fin: date) -> Optional[Dict]:
        """Obtiene KPIs para un período"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    WITH stats AS (
                        SELECT 
                            COUNT(DISTINCT r.id) as total_reservas,
                            COALESCE(SUM(r.tarifa_total), 0) as ingresos_totales,
                            AVG(r.fecha_check_out - r.fecha_check_in) as estancia_promedio,
                            COUNT(DISTINCT r.huesped_id) as huespedes_unicos,
                            SUM(CASE WHEN r.estado = 'cancelada' THEN 1 ELSE 0 END) as cancelaciones
                        FROM reservas r
                        WHERE r.fecha_reserva::date BETWEEN %s AND %s
                    ),
                    habitaciones_stats AS (
                        SELECT COUNT(*) as total_habitaciones, AVG(tarifa_base) as tarifa_promedio
                        FROM habitaciones WHERE activa = true
                    )
                    SELECT s.*, h.total_habitaciones, h.tarifa_promedio,
                        CASE WHEN s.total_reservas > 0 
                        THEN (s.cancelaciones::DECIMAL / s.total_reservas * 100) ELSE 0 END as tasa_cancelacion
                    FROM stats s, habitaciones_stats h
                """, (fecha_inicio, fecha_fin))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error en KPIs: {str(e)}")
            return None
