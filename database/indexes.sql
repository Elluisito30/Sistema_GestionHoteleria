-- ==================== ÍNDICES PARA OPTIMIZACIÓN ====================

-- Índices para búsquedas frecuentes
CREATE INDEX idx_reservas_fechas ON reservas(fecha_check_in, fecha_check_out);
CREATE INDEX idx_reservas_estado ON reservas(estado);
CREATE INDEX idx_reservas_huesped ON reservas(huesped_id);
CREATE INDEX idx_reservas_habitacion_fechas ON reservas(habitacion_id, fecha_check_in, fecha_check_out);

CREATE INDEX idx_huespedes_documento ON huespedes(numero_documento);
CREATE INDEX idx_huespedes_email ON huespedes(email);
CREATE INDEX idx_huespedes_nombre ON huespedes(nombre, apellido);

CREATE INDEX idx_habitaciones_numero ON habitaciones(numero);
CREATE INDEX idx_habitaciones_estado ON habitaciones(estado_id);
CREATE INDEX idx_habitaciones_tipo ON habitaciones(tipo_habitacion_id);

CREATE INDEX idx_facturas_numero ON facturas(numero_factura);
CREATE INDEX idx_facturas_fecha ON facturas(fecha_emision);
CREATE INDEX idx_facturas_estado ON facturas(estado);

CREATE INDEX idx_consumos_alojamiento ON consumos_servicios(alojamiento_id);
CREATE INDEX idx_detalle_factura ON detalle_factura(factura_id);

CREATE INDEX idx_logs_usuario_fecha ON logs_actividad(usuario_id, created_at);
CREATE INDEX idx_logs_accion ON logs_actividad(accion);

-- Índices de texto completo para búsquedas
CREATE INDEX idx_huespedes_busqueda ON huespedes USING GIN(
    to_tsvector('spanish', coalesce(nombre,'') || ' ' || coalesce(apellido,'') || ' ' || coalesce(numero_documento,''))
);