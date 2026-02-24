from typing import Dict, Any
from models.huesped import Huesped
from utils.logger import logger

class HuespedController:

    @staticmethod
    def buscar(termino: str):
        """Busca huéspedes por documento, email o nombre"""
        try:
            if not termino or len(termino.strip()) < 2:
                return []
            return Huesped.buscar(termino.strip())
        except Exception as e:
            logger.error(f"Error buscando huéspedes: {str(e)}")
            return []

    @staticmethod
    def crear_huesped(datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo huésped"""
        try:
            # Validar campos obligatorios
            if not datos.get('nombre') or not datos.get('apellido'):
                return {'success': False, 'error': 'Nombre y apellido son obligatorios'}
            if not datos.get('numero_documento'):
                return {'success': False, 'error': 'Número de documento es obligatorio'}

            # Verificar si ya existe por documento
            existente = Huesped.get_by_documento(datos['numero_documento'])
            if existente:
                return {
                    'success': True,
                    'huesped_id': existente['id'],
                    'mensaje': 'Huésped ya registrado'
                }

            # Crear instancia de Huesped con los campos actualizados
            huesped = Huesped(
                tipo_documento=datos.get('tipo_documento', 'DNI'),
                numero_documento=datos['numero_documento'],
                nombre=datos['nombre'],
                apellido=datos['apellido'],
                fecha_nacimiento=datos.get('fecha_nacimiento'),
                nacionalidad=datos.get('nacionalidad'),
                email=datos.get('email') or None,
                telefono=datos.get('telefono') or None,
                pais_origen=datos.get('pais_origen') or None,      # ← NUEVO
                ciudad_origen=datos.get('ciudad_origen') or None,  # ← NUEVO
                direccion=datos.get('direccion') or None,
                distrito=datos.get('distrito') or None,            # ← NUEVO
                codigo_postal=datos.get('codigo_postal') or None,
                preferencias=datos.get('preferencias') or None,
            )
            huesped_id = huesped.save()
            if huesped_id:
                logger.info(f"Huésped creado: {datos['nombre']} {datos['apellido']}")
                return {'success': True, 'huesped_id': huesped_id}
            return {'success': False, 'error': 'No se pudo guardar el huésped'}
        except Exception as e:
            logger.error(f"Error creando huésped: {str(e)}")
            return {'success': False, 'error': str(e)}