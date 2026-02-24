"""Controlador de facturas"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from config.database import db
from models.factura import Factura
from utils.logger import logger


class FacturaController:

    @staticmethod
    def crear_factura_desde_reserva(reserva_id: int, servicios_adicionales: List[Dict] = None) -> Dict[str, Any]:
        """Crea una factura automáticamente desde una reserva, calculando noches y totales"""
        try:
            from models.reserva import Reserva
            
            reserva = Reserva.get_by_id(reserva_id)
            if not reserva:
                return {'success': False, 'error': 'Reserva no encontrada'}
            
            # Calcular número de noches
            fecha_in = reserva['fecha_check_in']
            fecha_out = reserva['fecha_check_out']
            if isinstance(fecha_in, str):
                from datetime import datetime
                fecha_in = datetime.strptime(fecha_in, '%Y-%m-%d').date()
                fecha_out = datetime.strptime(fecha_out, '%Y-%m-%d').date()
            noches = (fecha_out - fecha_in).days
            
            # Calcular subtotal de alojamiento
            subtotal_alojamiento = reserva.get('tarifa_total', 0)
            
            # Calcular servicios adicionales
            subtotal_servicios = 0
            detalle_items = []
            
            # Agregar línea de alojamiento
            detalle_items.append({
                'concepto': f'Alojamiento - {noches} noche(s)',
                'cantidad': noches,
                'precio_unitario': subtotal_alojamiento / noches if noches > 0 else 0,
                'importe': subtotal_alojamiento,
                'tipo': 'alojamiento'
            })
            
            # Agregar servicios adicionales si existen
            if servicios_adicionales:
                for servicio in servicios_adicionales:
                    cantidad = servicio.get('cantidad', 1)
                    precio = servicio.get('precio_unitario', 0)
                    importe = cantidad * precio
                    subtotal_servicios += importe
                    
                    detalle_items.append({
                        'concepto': servicio.get('concepto', 'Servicio adicional'),
                        'cantidad': cantidad,
                        'precio_unitario': precio,
                        'importe': importe,
                        'tipo': servicio.get('tipo', 'servicio')
                    })
            
            # Calcular totales
            subtotal = subtotal_alojamiento + subtotal_servicios
            impuestos = subtotal * 0.10  # 10% de impuestos
            total = subtotal + impuestos
            
            # Crear factura
            datos_factura = {
                'huesped_id': reserva['huesped_id'],
                'reserva_id': reserva_id,
                'subtotal': subtotal,
                'impuestos': impuestos,
                'total': total,
                'estado': 'pendiente',
                'detalle': detalle_items
            }
            
            return FacturaController.crear_factura(datos_factura)
            
        except Exception as e:
            logger.error(f"Error creando factura desde reserva: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def crear_factura(datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva factura"""
        try:
            numero = Factura.generar_numero()
            with db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO facturas 
                    (numero_factura, huesped_id, reserva_id, subtotal, impuestos, total, metodo_pago, estado, notas)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, numero_factura
                """, (
                    numero,
                    datos.get('huesped_id'),
                    datos.get('reserva_id'),
                    datos.get('subtotal', 0),
                    datos.get('impuestos', 0),
                    datos.get('total', 0),
                    datos.get('metodo_pago'),
                    datos.get('estado', 'pendiente'),
                    datos.get('notas')
                ))
                result = cursor.fetchone()

                # Insertar líneas de detalle si existen
                if datos.get('detalle'):
                    for item in datos['detalle']:
                        cursor.execute("""
                            INSERT INTO detalle_factura 
                            (factura_id, concepto, cantidad, precio_unitario, importe, tipo)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            result['id'],
                            item.get('concepto', ''),
                            item.get('cantidad', 1),
                            item.get('precio_unitario', 0),
                            item.get('importe', 0),
                            item.get('tipo', 'alojamiento')
                        ))

                return {
                    'success': True,
                    'factura_id': result['id'],
                    'numero_factura': result['numero_factura']
                }
        except Exception as e:
            logger.error(f"Error creando factura: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_by_reserva(reserva_id: int) -> List[dict]:
        """Obtiene facturas asociadas a una reserva"""
        return Factura.get_by_reserva(reserva_id)

    @staticmethod
    def marcar_pagada(factura_id: int, metodo_pago: str = None) -> bool:
        """Marca una factura como pagada"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE facturas 
                    SET estado = 'pagada', fecha_pago = CURRENT_TIMESTAMP, metodo_pago = COALESCE(%s, metodo_pago)
                    WHERE id = %s
                    RETURNING id
                """, (metodo_pago, factura_id))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error marcando factura como pagada: {str(e)}")
            return False
