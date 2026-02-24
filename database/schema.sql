-- =====================================================
-- SISTEMA DE GESTIÓN HOTELERA - ESQUEMA COMPLETO
-- =====================================================

-- Extensión para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== TABLAS BASE ====================

-- Catálogo de tipos de habitación
CREATE TABLE tipos_habitacion (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    capacidad_maxima INTEGER NOT NULL CHECK (capacidad_maxima > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Catálogo de estados de habitación
CREATE TABLE estados_habitacion (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE, -- disponible, ocupada, mantenimiento, reservada, limpieza
    descripcion TEXT,
    color_hex VARCHAR(7) -- Para UI
);

-- Habitaciones
CREATE TABLE habitaciones (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(10) NOT NULL UNIQUE,
    piso INTEGER NOT NULL,
    tipo_habitacion_id INTEGER REFERENCES tipos_habitacion(id),
    estado_id INTEGER REFERENCES estados_habitacion(id) DEFAULT 1,
    tarifa_base DECIMAL(10,2) NOT NULL CHECK (tarifa_base > 0),
    tiene_vista BOOLEAN DEFAULT FALSE,
    tiene_balcon BOOLEAN DEFAULT FALSE,
    metros_cuadrados DECIMAL(5,2),
    notas TEXT,
    activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Características adicionales de habitaciones
CREATE TABLE caracteristicas_habitacion (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    icono VARCHAR(50) -- Para UI
);

-- Relación habitaciones-características
CREATE TABLE habitacion_caracteristicas (
    habitacion_id INTEGER REFERENCES habitaciones(id) ON DELETE CASCADE,
    caracteristica_id INTEGER REFERENCES caracteristicas_habitacion(id) ON DELETE CASCADE,
    PRIMARY KEY (habitacion_id, caracteristica_id)
);

-- Tarifas dinámicas por temporada
CREATE TABLE temporadas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    factor_multipliador DECIMAL(3,2) DEFAULT 1.0,
    descripcion TEXT,
    CHECK (fecha_inicio <= fecha_fin)
);

-- Tarifas especiales por tipo de habitación y temporada
CREATE TABLE tarifas_temporada (
    id SERIAL PRIMARY KEY,
    tipo_habitacion_id INTEGER REFERENCES tipos_habitacion(id),
    temporada_id INTEGER REFERENCES temporadas(id),
    tarifa_especial DECIMAL(10,2),
    UNIQUE(tipo_habitacion_id, temporada_id)
);

-- Huéspedes
CREATE TABLE huespedes (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    tipo_documento VARCHAR(20) NOT NULL, -- DNI, Pasaporte, etc
    numero_documento VARCHAR(30) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    nacionalidad VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    telefono VARCHAR(20),
    direccion TEXT,
    ciudad VARCHAR(100),
    pais VARCHAR(50),
    codigo_postal VARCHAR(20),
    preferencias TEXT,
    es_vip BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reservas
CREATE TABLE reservas (
    id SERIAL PRIMARY KEY,
    codigo_reserva VARCHAR(20) UNIQUE NOT NULL,
    huesped_id INTEGER REFERENCES huespedes(id),
    fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_check_in DATE NOT NULL,
    fecha_check_out DATE NOT NULL,
    numero_adultos INTEGER DEFAULT 1 CHECK (numero_adultos >= 0),
    numero_ninos INTEGER DEFAULT 0 CHECK (numero_ninos >= 0),
    estado VARCHAR(30) DEFAULT 'confirmada', -- confirmada, cancelada, completada, no_show
    habitacion_id INTEGER REFERENCES habitaciones(id),
    tarifa_total DECIMAL(10,2) NOT NULL,
    deposito_requerido DECIMAL(10,2) DEFAULT 0,
    deposito_pagado BOOLEAN DEFAULT FALSE,
    notas TEXT,
    politicas_cancelacion TEXT,
    fecha_cancelacion TIMESTAMP,
    motivo_cancelacion TEXT,
    created_by INTEGER, -- usuario_id
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (fecha_check_in < fecha_check_out)
);

-- Historial de estados de reserva
CREATE TABLE historial_estados_reserva (
    id SERIAL PRIMARY KEY,
    reserva_id INTEGER REFERENCES reservas(id) ON DELETE CASCADE,
    estado_anterior VARCHAR(30),
    estado_nuevo VARCHAR(30) NOT NULL,
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER,
    motivo TEXT
);

-- Registro de alojamiento (Check-in/Check-out)
CREATE TABLE alojamientos (
    id SERIAL PRIMARY KEY,
    reserva_id INTEGER UNIQUE REFERENCES reservas(id),
    habitacion_asignada_id INTEGER REFERENCES habitaciones(id),
    fecha_check_in TIMESTAMP,
    fecha_check_out TIMESTAMP,
    llave_entregada BOOLEAN DEFAULT FALSE,
    llave_devuelta BOOLEAN DEFAULT FALSE,
    observaciones_check_in TEXT,
    observaciones_check_out TEXT,
    usuario_check_in INTEGER,
    usuario_check_out INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Servicios adicionales
CREATE TABLE servicios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio_base DECIMAL(10,2) NOT NULL,
    categoria VARCHAR(50), -- restaurante, lavandería, spa, minibar, etc
    activo BOOLEAN DEFAULT TRUE
);

-- Consumos de servicios durante la estancia
CREATE TABLE consumos_servicios (
    id SERIAL PRIMARY KEY,
    alojamiento_id INTEGER REFERENCES alojamientos(id),
    servicio_id INTEGER REFERENCES servicios(id),
    cantidad INTEGER DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL,
    fecha_consumo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notas TEXT
);

-- Facturas
CREATE TABLE facturas (
    id SERIAL PRIMARY KEY,
    numero_factura VARCHAR(20) UNIQUE NOT NULL,
    huesped_id INTEGER REFERENCES huespedes(id),
    reserva_id INTEGER REFERENCES reservas(id),
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_pago TIMESTAMP,
    subtotal DECIMAL(10,2) NOT NULL,
    impuestos DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    metodo_pago VARCHAR(50),
    estado VARCHAR(30) DEFAULT 'pendiente', -- pendiente, pagada, cancelada, reembolsada
    notas TEXT
);

-- Detalle de factura
CREATE TABLE detalle_factura (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER REFERENCES facturas(id) ON DELETE CASCADE,
    concepto VARCHAR(200) NOT NULL,
    cantidad INTEGER DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL,
    importe DECIMAL(10,2) NOT NULL,
    tipo VARCHAR(50) -- alojamiento, servicio, cargo_extra
);

-- Usuarios del sistema
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    rol VARCHAR(30) DEFAULT 'recepcionista', -- admin, gerente, recepcionista, mantenimiento
    activo BOOLEAN DEFAULT TRUE,
    ultimo_acceso TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Logs de actividades
CREATE TABLE logs_actividad (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    accion VARCHAR(100) NOT NULL,
    entidad VARCHAR(50),
    entidad_id INTEGER,
    detalles JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== FUNCIONES Y TRIGGERS ====================

-- Función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_tipos_habitacion_updated_at BEFORE UPDATE ON tipos_habitacion
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_habitaciones_updated_at BEFORE UPDATE ON habitaciones
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_huespedes_updated_at BEFORE UPDATE ON huespedes
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_reservas_updated_at BEFORE UPDATE ON reservas
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Secuencia para códigos de reserva
CREATE SEQUENCE IF NOT EXISTS reservas_codigo_seq;

-- Función para generar código de reserva automático
CREATE OR REPLACE FUNCTION generar_codigo_reserva()
RETURNS TRIGGER AS $$
DECLARE
    codigo VARCHAR(20);
    prefijo VARCHAR(3) := 'RES';
    numero INT;
BEGIN
    numero := nextval('reservas_codigo_seq');
    codigo := prefijo || LPAD(numero::TEXT, 6, '0');
    NEW.codigo_reserva := codigo;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_generar_codigo_reserva
    BEFORE INSERT ON reservas
    FOR EACH ROW
    EXECUTE PROCEDURE generar_codigo_reserva();

-- Función para verificar disponibilidad de habitación
CREATE OR REPLACE FUNCTION verificar_disponibilidad(
    p_habitacion_id INTEGER,
    p_check_in DATE,
    p_check_out DATE,
    p_reserva_id_excluir INTEGER DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    conflictos INTEGER;
BEGIN
    SELECT COUNT(*) INTO conflictos
    FROM reservas r
    WHERE r.habitacion_id = p_habitacion_id
        AND r.estado NOT IN ('cancelada', 'completada')
        AND (p_reserva_id_excluir IS NULL OR r.id != p_reserva_id_excluir)
        AND (
            (p_check_in BETWEEN r.fecha_check_in AND r.fecha_check_out - INTERVAL '1 day')
            OR (p_check_out - INTERVAL '1 day' BETWEEN r.fecha_check_in AND r.fecha_check_out - INTERVAL '1 day')
            OR (r.fecha_check_in BETWEEN p_check_in AND p_check_out - INTERVAL '1 day')
        );
    
    RETURN conflictos = 0;
END;
$$ LANGUAGE plpgsql;