from dataclasses import dataclass
from typing import Optional, List
from datetime import date
from config.database import db

@dataclass
class Habitacion:
    id: Optional[int] = None
    numero: str = ""
    piso: int = 0
    tipo_habitacion_id: int = 0
    estado_id: int = 1
    tarifa_base: float = 0.0
    tiene_vista: bool = False
    tiene_balcon: bool = False
    metros_cuadrados: Optional[float] = None
    notas: Optional[str] = None
    activa: bool = True
    
    @classmethod
    def get_by_id(cls, habitacion_id: int):
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT h.*, th.nombre as tipo_nombre, eh.nombre as estado_nombre,
                       th.capacidad_maxima
                FROM habitaciones h
                JOIN tipos_habitacion th ON h.tipo_habitacion_id = th.id
                JOIN estados_habitacion eh ON h.estado_id = eh.id
                WHERE h.id = %s
            """, (habitacion_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    @classmethod
    def get_all(cls, activas_only: bool = True):
        with db.get_cursor() as cursor:
            query = """
                SELECT h.*, th.nombre as tipo_nombre, th.capacidad_maxima,
                       eh.nombre as estado_nombre, eh.color_hex as estado_color
                FROM habitaciones h
                JOIN tipos_habitacion th ON h.tipo_habitacion_id = th.id
                JOIN estados_habitacion eh ON h.estado_id = eh.id
            """
            if activas_only:
                query += " WHERE h.activa = true"
            query += " ORDER BY h.piso, h.numero"
            
            cursor.execute(query)
            return cursor.fetchall()
    
    @classmethod
    def get_disponibles(cls, check_in: date, check_out: date, tipo_id: Optional[int] = None):
        """
        Retorna habitaciones disponibles para las fechas indicadas
        Usa la función verificar_disponibilidad() de PostgreSQL para mayor precisión
        """
        print("\n" + "="*50)
        print(f"🔍 MODELO HABITACION: get_disponibles()")
        print(f"📅 check_in: {check_in}")
        print(f"📅 check_out: {check_out}")
        print(f"🏷️ tipo_id: {tipo_id}")
        print("="*50)
        
        try:
            with db.get_cursor() as cursor:
                query = """
                    SELECT h.*, th.nombre as tipo_nombre, th.capacidad_maxima
                    FROM habitaciones h
                    JOIN tipos_habitacion th ON h.tipo_habitacion_id = th.id
                    WHERE h.activa = true 
                      AND h.estado_id = (SELECT id FROM estados_habitacion WHERE nombre = 'disponible')
                      AND verificar_disponibilidad(h.id, %s, %s, NULL) = true
                """
                params = [check_in, check_out]
                
                if tipo_id:
                    query += " AND h.tipo_habitacion_id = %s"
                    params.append(tipo_id)
                
                query += " ORDER BY h.piso, h.numero"
                
                # Mostrar la query con parámetros (para depuración)
                try:
                    from psycopg2 import sql
                    print(f"📝 Query ejecutada: {cursor.mogrify(query, params).decode()}")
                except:
                    print(f"📝 Query: {query}")
                    print(f"📦 Params: {params}")
                
                cursor.execute(query, params)
                resultados = cursor.fetchall()
                
                print(f"✅ Resultados encontrados: {len(resultados)} habitaciones")
                
                # Mostrar cada habitación encontrada
                if resultados:
                    for r in resultados:
                        print(f"   - Hab {r['numero']} | {r['tipo_nombre']} | Piso {r['piso']} | €{r['tarifa_base']}")
                else:
                    print("   ⚠️ No se encontraron habitaciones")
                
                print("="*50 + "\n")
                return resultados
                
        except Exception as e:
            print(f"❌ ERROR en get_disponibles: {str(e)}")
            import traceback
            traceback.print_exc()
            print("="*50 + "\n")
            return []
    
    def save(self):
        with db.get_cursor() as cursor:
            if self.id:
                cursor.execute("""
                    UPDATE habitaciones 
                    SET numero = %s, piso = %s, tipo_habitacion_id = %s,
                        estado_id = %s, tarifa_base = %s, tiene_vista = %s,
                        tiene_balcon = %s, metros_cuadrados = %s, notas = %s,
                        activa = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id
                """, (self.numero, self.piso, self.tipo_habitacion_id,
                      self.estado_id, self.tarifa_base, self.tiene_vista,
                      self.tiene_balcon, self.metros_cuadrados, self.notas,
                      self.activa, self.id))
            else:
                cursor.execute("""
                    INSERT INTO habitaciones 
                    (numero, piso, tipo_habitacion_id, estado_id, tarifa_base,
                     tiene_vista, tiene_balcon, metros_cuadrados, notas, activa)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (self.numero, self.piso, self.tipo_habitacion_id,
                      self.estado_id, self.tarifa_base, self.tiene_vista,
                      self.tiene_balcon, self.metros_cuadrados, self.notas,
                      self.activa))
            
            result = cursor.fetchone()
            return result['id'] if result else None
    
    def update_estado(self, nuevo_estado_id: int):
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE habitaciones 
                SET estado_id = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id
            """, (nuevo_estado_id, self.id))
            return cursor.fetchone() is not None