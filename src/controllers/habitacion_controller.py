"""Controlador de habitaciones"""
from typing import List, Dict, Optional
from models.habitacion import Habitacion
from utils.logger import logger


class HabitacionController:
    """Controlador para operaciones de habitaciones"""

    @staticmethod
    def get_all(activas_only: bool = True) -> List[Dict]:
        """Obtiene todas las habitaciones"""
        try:
            return Habitacion.get_all(activas_only=activas_only)
        except Exception as e:
            logger.error(f"Error obteniendo habitaciones: {str(e)}")
            return []

    @staticmethod
    def get_by_id(habitacion_id: int) -> Optional[Dict]:
        """Obtiene una habitación por ID"""
        try:
            return Habitacion.get_by_id(habitacion_id)
        except Exception as e:
            logger.error(f"Error obteniendo habitación {habitacion_id}: {str(e)}")
            return None

    @staticmethod
    def get_disponibles(check_in, check_out, tipo_id: Optional[int] = None) -> List[Dict]:
        """Obtiene habitaciones disponibles para un rango de fechas"""
        try:
            return Habitacion.get_disponibles(check_in, check_out, tipo_id)
        except Exception as e:
            logger.error(f"Error obteniendo habitaciones disponibles: {str(e)}")
            return []

    @staticmethod
    def update_estado(habitacion_id: int, nuevo_estado_id: int) -> bool:
        """Actualiza el estado de una habitación"""
        try:
            habitacion = Habitacion(id=habitacion_id)
            return habitacion.update_estado(nuevo_estado_id)
        except Exception as e:
            logger.error(f"Error actualizando estado de habitación {habitacion_id}: {str(e)}")
            return False
