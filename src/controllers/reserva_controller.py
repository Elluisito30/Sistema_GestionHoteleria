# src/controllers/reserva_controller.py
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from models.reserva import Reserva
from models.habitacion import Habitacion
from models.huesped import Huesped
from config.database import db
from utils.logger import logger

class ReservaController:
    
    @staticmethod
    def crear_reserva(datos_reserva: Dict[str, Any], usuario_id: int) -> Dict[str, Any]:
        """
        Crea una nueva reserva con validaciones
        """
        try:
            # Validar fechas
            check_in = datos_reserva.get('fecha_check_in')
            check_out = datos_reserva.get('fecha_check_out')
            
            if check_in >= check_out:
                return {
                    'success': False,
                    'error': 'La fecha de check-out debe ser posterior al check-in'
                }
            
            if check_in < date.today():
                return {
                    'success': False,
                    'error': 'La fecha de check-in no puede ser en el pasado'
                }
            
            # Validar capacidad
            habitacion = Habitacion.get_by_id(datos_reserva.get('habitacion_id'))
            if habitacion:
                capacidad_maxima = habitacion.get('capacidad_maxima', 2)
                total_personas = datos_reserva.get('numero_adultos', 1) + datos_reserva.get('numero_ninos', 0)
                
                if total_personas > capacidad_maxima:
                    return {
                        'success': False,
                        'error': f'La habitación solo tiene capacidad para {capacidad_maxima} personas'
                    }
            
            # Crear reserva
            reserva = Reserva(
                huesped_id=datos_reserva['huesped_id'],
                fecha_check_in=check_in,
                fecha_check_out=check_out,
                numero_adultos=datos_reserva.get('numero_adultos', 1),
                numero_ninos=datos_reserva.get('numero_ninos', 0),
                habitacion_id=datos_reserva.get('habitacion_id'),
                tarifa_total=datos_reserva.get('tarifa_total', 0),
                notas=datos_reserva.get('notas')
            )
            
            # Verificar disponibilidad
            if not reserva.check_disponibilidad():
                return {
                    'success': False,
                    'error': 'La habitación no está disponible para las fechas seleccionadas'
                }
            
            reserva_id = reserva.save(usuario_id)
            
            logger.info(f"Reserva creada: {reserva.codigo_reserva} por usuario {usuario_id}")
            
            return {
                'success': True,
                'reserva_id': reserva_id,
                'codigo_reserva': reserva.codigo_reserva
            }
            
        except Exception as e:
            logger.error(f"Error al crear reserva: {str(e)}")
            return {
                'success': False,
                'error': f'Error al crear la reserva: {str(e)}'
            }
    
    @staticmethod
    def buscar_disponibilidad(check_in: date, check_out: date, 
                             tipo_habitacion: Optional[int] = None,
                             capacidad: Optional[int] = None) -> List[Dict]:
        """
        Busca habitaciones disponibles según criterios
        """
        print("\n" + "🔥"*60)
        print("🔥 CONTROLLER: buscar_disponibilidad() - INICIO")
        print(f"🔥 check_in: {check_in} ({type(check_in)})")
        print(f"🔥 check_out: {check_out} ({type(check_out)})")
        print(f"🔥 tipo_habitacion: {tipo_habitacion} ({type(tipo_habitacion)})")
        print(f"🔥 capacidad: {capacidad} ({type(capacidad)})")
        print("🔥"*60)
        
        try:
            # PASO 1: Llamar al modelo
            print("\n📞 CONTROLLER: Llamando a Habitacion.get_disponibles()...")
            habitaciones = Habitacion.get_disponibles(check_in, check_out, tipo_habitacion)
            
            print(f"📞 CONTROLLER: get_disponibles devolvió {len(habitaciones)} habitaciones")
            
            # Mostrar las habitaciones recibidas del modelo
            if habitaciones:
                print("📋 Habitaciones recibidas del modelo:")
                for h in habitaciones:
                    print(f"   - ID: {h.get('id')} | N°: {h.get('numero')} | Tipo: {h.get('tipo_nombre')} | Capacidad: {h.get('capacidad_maxima')}")
            else:
                print("⚠️ El modelo NO devolvió ninguna habitación")
            
            # PASO 2: Filtrar por capacidad si se especifica
            if capacidad and habitaciones:
                original_count = len(habitaciones)
                print(f"\n🔧 CONTROLLER: Filtrando por capacidad mínima {capacidad} personas...")
                
                habitaciones = [
                    h for h in habitaciones 
                    if h.get('capacidad_maxima', 0) >= capacidad
                ]
                
                print(f"🔧 CONTROLLER: {original_count} → {len(habitaciones)} habitaciones después del filtro")
                
                if len(habitaciones) < original_count:
                    print("   Habitaciones filtradas por capacidad:")
                    for h in habitaciones:
                        print(f"   - Hab {h.get('numero')} (Capacidad: {h.get('capacidad_maxima')})")
            
            # PASO 3: Calcular tarifas según temporada
            if habitaciones:
                print(f"\n💰 CONTROLLER: Calculando tarifas para {len(habitaciones)} habitaciones...")
                for habitacion in habitaciones:
                    # Convertir tarifa_base a float ANTES de pasarla a la función
                    tarifa_base = habitacion['tarifa_base']
                    if hasattr(tarifa_base, 'item'):
                        tarifa_base = float(tarifa_base)
                    elif not isinstance(tarifa_base, (int, float)):
                        tarifa_base = float(tarifa_base)
                    
                    tarifa = ReservaController._calcular_tarifa(
                        tarifa_base,
                        check_in,
                        check_out
                    )
                    habitacion['tarifa_calculada'] = tarifa
                    habitacion['total_estancia'] = tarifa * (check_out - check_in).days
                    print(f"   - Hab {habitacion['numero']}: tarifa_base={habitacion['tarifa_base']}, calculada={tarifa:.2f}")
            
            print(f"\n✅ CONTROLLER: Devolviendo {len(habitaciones)} habitaciones a la vista")
            print("🔥"*60 + "\n")
            
            return habitaciones
            
        except Exception as e:
            print(f"\n❌ ERROR en CONTROLLER: {str(e)}")
            import traceback
            traceback.print_exc()
            print("🔥"*60 + "\n")
            logger.error(f"Error en búsqueda de disponibilidad: {str(e)}")
            return []
    
    @staticmethod
    def _calcular_tarifa(tarifa_base: float, check_in: date, check_out: date) -> float:
        """
        Calcula la tarifa aplicando factores de temporada
        - Ahora maneja correctamente tipos Decimal convirtiendo a float
        """
        from models.temporada import Temporada
        
        # Asegurar que tarifa_base sea float (por si acaso)
        try:
            tarifa_base = float(tarifa_base)
        except (TypeError, ValueError):
            tarifa_base = 0.0
            
        dias = (check_out - check_in).days
        if dias == 0:
            return 0.0
            
        tarifa_total = 0.0
        
        for i in range(dias):
            fecha_actual = check_in + timedelta(days=i)
            factor = Temporada.get_factor_for_date(fecha_actual)
            
            # Convertir factor a float si es necesario
            try:
                factor = float(factor)
            except (TypeError, ValueError):
                factor = 1.0
                
            tarifa_total += tarifa_base * factor
        
        return round(tarifa_total / dias, 2)  # Tarifa promedio por día
    
    @staticmethod
    def check_in(reserva_id: int, habitacion_id: int, usuario_id: int) -> Dict[str, Any]:
        """
        Procesa el check-in de una reserva
        """
        try:
            with db.get_cursor() as cursor:
                # Verificar que la reserva existe y está confirmada
                cursor.execute("""
                    SELECT r.*, h.estado_id 
                    FROM reservas r
                    JOIN habitaciones h ON r.habitacion_id = h.id
                    WHERE r.id = %s
                """, (reserva_id,))
                
                reserva = cursor.fetchone()
                
                if not reserva:
                    return {'success': False, 'error': 'Reserva no encontrada'}
                
                if reserva['estado'] != 'confirmada':
                    return {'success': False, 'error': 'La reserva no está confirmada'}
                
                # Verificar que la habitación está disponible
                if reserva['estado_id'] != 1:  # 1 = disponible
                    return {'success': False, 'error': 'La habitación no está disponible'}
                
                # Crear registro de alojamiento
                cursor.execute("""
                    INSERT INTO alojamientos 
                    (reserva_id, habitacion_asignada_id, fecha_check_in, 
                     llave_entregada, usuario_check_in)
                    VALUES (%s, %s, CURRENT_TIMESTAMP, true, %s)
                    RETURNING id
                """, (reserva_id, habitacion_id, usuario_id))
                
                alojamiento_id = cursor.fetchone()['id']
                
                # Actualizar estado de la reserva
                cursor.execute("""
                    UPDATE reservas 
                    SET estado = 'completada'
                    WHERE id = %s
                """, (reserva_id,))
                
                # Actualizar estado de la habitación
                cursor.execute("""
                    UPDATE habitaciones 
                    SET estado_id = 2  -- ocupada
                    WHERE id = %s
                """, (habitacion_id,))
                
                # Registrar en historial
                cursor.execute("""
                    INSERT INTO historial_estados_reserva 
                    (reserva_id, estado_anterior, estado_nuevo, usuario_id, motivo)
                    VALUES (%s, 'confirmada', 'completada', %s, 'Check-in realizado')
                """, (reserva_id, usuario_id))
                
                logger.info(f"Check-in realizado: Reserva {reserva_id}, Habitación {habitacion_id}")
                
                return {
                    'success': True,
                    'alojamiento_id': alojamiento_id,
                    'mensaje': 'Check-in realizado exitosamente'
                }
                
        except Exception as e:
            logger.error(f"Error en check-in: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def check_out(reserva_id: int, habitacion_id: int, usuario_id: int, observaciones: str = None) -> Dict[str, Any]:
        """
        Procesa el check-out de una reserva
        """
        try:
            with db.get_cursor() as cursor:
                # Verificar que existe el alojamiento
                cursor.execute("""
                    SELECT a.*, r.estado as estado_reserva
                    FROM alojamientos a
                    JOIN reservas r ON a.reserva_id = r.id
                    WHERE a.reserva_id = %s
                """, (reserva_id,))
                
                alojamiento = cursor.fetchone()
                
                if not alojamiento:
                    return {'success': False, 'error': 'No se encontró el registro de alojamiento'}
                
                if alojamiento['fecha_check_out']:
                    return {'success': False, 'error': 'El check-out ya fue realizado'}
                
                # Actualizar alojamiento con fecha de check-out
                cursor.execute("""
                    UPDATE alojamientos 
                    SET fecha_check_out = CURRENT_TIMESTAMP,
                        llave_devuelta = true,
                        usuario_check_out = %s,
                        observaciones_check_out = %s
                    WHERE reserva_id = %s
                    RETURNING id
                """, (usuario_id, observaciones, reserva_id))
                
                # Actualizar estado de la habitación a disponible
                cursor.execute("""
                    UPDATE habitaciones 
                    SET estado_id = 1  -- disponible
                    WHERE id = %s
                """, (habitacion_id,))
                
                # Registrar en historial
                cursor.execute("""
                    INSERT INTO historial_estados_reserva 
                    (reserva_id, estado_anterior, estado_nuevo, usuario_id, motivo)
                    VALUES (%s, 'completada', 'completada', %s, 'Check-out realizado')
                """, (reserva_id, usuario_id))
                
                logger.info(f"Check-out realizado: Reserva {reserva_id}, Habitación {habitacion_id}")
                
                return {
                    'success': True,
                    'mensaje': 'Check-out realizado exitosamente'
                }
                
        except Exception as e:
            logger.error(f"Error en check-out: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ==================== NUEVO MÉTODO ====================
    @staticmethod
    def cancelar_reserva(reserva_id: int, motivo: str, usuario_id: int, aplicar_reembolso: bool = False) -> Dict[str, Any]:
        """
        Cancela una reserva existente
        """
        try:
            with db.get_cursor() as cursor:
                # Verificar que la reserva existe
                cursor.execute("""
                    SELECT r.*, h.estado_id, h.numero as habitacion_numero
                    FROM reservas r
                    JOIN habitaciones h ON r.habitacion_id = h.id
                    WHERE r.id = %s
                """, (reserva_id,))
                
                reserva = cursor.fetchone()
                
                if not reserva:
                    return {'success': False, 'error': 'Reserva no encontrada'}
                
                # Verificar que la reserva puede cancelarse
                if reserva['estado'] in ['cancelada', 'completada']:
                    return {'success': False, 'error': f'La reserva ya está {reserva["estado"]}'}
                
                # Guardar estado anterior para historial
                estado_anterior = reserva['estado']
                
                # Actualizar reserva
                cursor.execute("""
                    UPDATE reservas 
                    SET estado = 'cancelada',
                        fecha_cancelacion = CURRENT_TIMESTAMP,
                        motivo_cancelacion = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id
                """, (motivo, reserva_id))
                
                resultado = cursor.fetchone()
                
                if not resultado:
                    return {'success': False, 'error': 'No se pudo cancelar la reserva'}
                
                # Registrar en historial
                cursor.execute("""
                    INSERT INTO historial_estados_reserva 
                    (reserva_id, estado_anterior, estado_nuevo, usuario_id, motivo)
                    VALUES (%s, %s, 'cancelada', %s, %s)
                """, (reserva_id, estado_anterior, usuario_id, motivo))
                
                # Si aplica reembolso, registrar en logs
                if aplicar_reembolso and reserva.get('deposito_pagado', False):
                    cursor.execute("""
                        INSERT INTO logs_actividad 
                        (usuario_id, accion, entidad, entidad_id, detalles)
                        VALUES (%s, 'REEMBOLSO', 'reserva', %s, %s)
                    """, (usuario_id, reserva_id, 
                          f'{{"motivo": "{motivo}", "monto": {reserva.get("deposito_requerido", 0)}}}'))
                    
                    logger.info(f"Reembolso registrado para reserva {reserva_id}, monto: {reserva.get('deposito_requerido', 0)}")
                
                logger.info(f"Reserva cancelada: ID {reserva_id}, motivo: {motivo}, usuario: {usuario_id}")
                
                return {
                    'success': True,
                    'mensaje': 'Reserva cancelada exitosamente',
                    'codigo_reserva': reserva['codigo_reserva']
                }
                
        except Exception as e:
            logger.error(f"Error cancelando reserva: {str(e)}")
            return {'success': False, 'error': f'Error al cancelar: {str(e)}'}