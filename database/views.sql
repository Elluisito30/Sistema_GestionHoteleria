-- ==================== VISTAS PARA REPORTES ====================

-- =========================================
-- Vista de ocupación diaria (hoy)
-- =========================================
CREATE OR REPLACE VIEW vw_ocupacion_diaria AS
SELECT 
    CURRENT_DATE as fecha,
    COUNT(DISTINCT r.id) as reservas_activas,
    COUNT(DISTINCT r.habitacion_id) as habitaciones_ocupadas,
    (SELECT COUNT(*) FROM habitaciones WHERE activa = true) as total_habitaciones,
    ROUND(
        (
            COUNT(DISTINCT r.habitacion_id)::DECIMAL /
            NULLIF((SELECT COUNT(*) FROM habitaciones WHERE activa = true), 0)
        ) * 100
    , 2) as porcentaje_ocupacion
FROM reservas r
WHERE r.estado IN ('confirmada', 'completada')
    AND r.fecha_check_in <= CURRENT_DATE
    AND r.fecha_check_out > CURRENT_DATE;



-- =========================================
-- Vista de ingresos por período (mensual)
-- =========================================
CREATE OR REPLACE VIEW vw_ingresos_periodo AS
SELECT 
    DATE_TRUNC('month', f.fecha_emision) as periodo,
    COUNT(DISTINCT f.id) as total_facturas,
    COALESCE(SUM(f.total), 0) as ingresos_totales,
    COALESCE(AVG(f.total), 0) as ticket_promedio,
    SUM(CASE WHEN f.metodo_pago = 'efectivo' THEN f.total ELSE 0 END) as ingresos_efectivo,
    SUM(CASE WHEN f.metodo_pago = 'tarjeta' THEN f.total ELSE 0 END) as ingresos_tarjeta,
    SUM(CASE WHEN f.metodo_pago = 'transferencia' THEN f.total ELSE 0 END) as ingresos_transferencia
FROM facturas f
WHERE f.estado = 'pagada'
GROUP BY DATE_TRUNC('month', f.fecha_emision)
ORDER BY periodo DESC;



-- =========================================
-- Vista de KPIs principales
-- =========================================
CREATE OR REPLACE VIEW vw_kpis_hotel AS
WITH ocupacion_actual AS (
    SELECT COUNT(DISTINCT habitacion_id) as ocupadas_hoy
    FROM reservas
    WHERE estado IN ('confirmada', 'completada')
        AND fecha_check_in <= CURRENT_DATE
        AND fecha_check_out > CURRENT_DATE
),
ingresos_mes AS (
    SELECT COALESCE(SUM(total), 0) as ingresos_mes_actual
    FROM facturas
    WHERE estado = 'pagada'
        AND DATE_TRUNC('month', fecha_emision) = DATE_TRUNC('month', CURRENT_DATE)
),
estancia_promedio AS (
    SELECT COALESCE(AVG(fecha_check_out - fecha_check_in), 0) as promedio_dias
    FROM reservas
    WHERE fecha_check_out >= CURRENT_DATE - INTERVAL '30 days'
        AND estado = 'completada'
)
SELECT 
    (SELECT ocupadas_hoy FROM ocupacion_actual) as habitaciones_ocupadas_hoy,

    (SELECT COUNT(*) FROM habitaciones WHERE activa = true) as total_habitaciones,

    ROUND(
        (
            (SELECT ocupadas_hoy FROM ocupacion_actual)::DECIMAL /
            NULLIF((SELECT COUNT(*) FROM habitaciones WHERE activa = true), 0)
        ) * 100
    , 2) as porcentaje_ocupacion_hoy,

    (SELECT COUNT(*) 
     FROM reservas 
     WHERE fecha_reserva::date = CURRENT_DATE) as reservas_hoy,

    (SELECT COUNT(*) 
     FROM huespedes 
     WHERE created_at::date = CURRENT_DATE) as nuevos_huespedes_hoy,

    (SELECT ingresos_mes_actual FROM ingresos_mes) as ingresos_mes_actual,

    (SELECT promedio_dias FROM estancia_promedio) as estancia_promedio_dias;



-- =========================================
-- Vista de tendencias por temporada
-- =========================================
CREATE OR REPLACE VIEW vw_tendencias_temporada AS
SELECT 
    t.nombre as temporada,
    COUNT(r.id) as total_reservas,
    COALESCE(AVG(r.tarifa_total), 0) as tarifa_promedio,
    COALESCE(SUM(r.tarifa_total), 0) as ingresos_totales,
    COALESCE(AVG(r.fecha_check_out - r.fecha_check_in), 0) as duracion_promedio_dias
FROM reservas r
JOIN temporadas t 
    ON r.fecha_check_in BETWEEN t.fecha_inicio AND t.fecha_fin
WHERE r.estado NOT IN ('cancelada', 'no_show')
GROUP BY t.id, t.nombre;
