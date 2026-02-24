from typing import Optional
from datetime import date
from config.database import db


class Temporada:
    """Modelo para tarifas por temporada"""

    @staticmethod
    def get_factor_for_date(fecha: date) -> float:
        """
        Obtiene el factor multiplicador de tarifa para una fecha dada.
        Retorna 1.0 si no hay temporada definida.
        """
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT factor_multipliador 
                FROM temporadas 
                WHERE %s BETWEEN fecha_inicio AND fecha_fin
                ORDER BY factor_multipliador DESC
                LIMIT 1
            """, (fecha,))
            result = cursor.fetchone()
            return float(result['factor_multipliador']) if result else 1.0
