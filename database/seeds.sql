-- =====================================================
-- 🌟 SISTEMA HOTELERO - DATOS COMPLETOS
-- =====================================================

-- =====================================================
-- 🏨 1. DATOS BASE (CATÁLOGOS)
-- =====================================================

-- Tipos de habitación (PRIMERO)
INSERT INTO tipos_habitacion (nombre, descripcion, capacidad_maxima) VALUES
('Individual', 'Habitación con cama individual, ideal para viajeros solos', 1),
('Doble', 'Habitación con cama matrimonial o dos camas individuales', 2),
('Suite', 'Habitación de lujo con sala de estar separada', 4),
('Familiar', 'Habitación amplia para familias, con camas adicionales', 5),
('Presidencial', 'La máxima experiencia de lujo, con todas las comodidades', 6);

-- Estados de habitación
INSERT INTO estados_habitacion (nombre, descripcion, color_hex) VALUES
('disponible', 'Habitación libre y lista para uso', '#28a745'),
('ocupada', 'Habitación con huéspedes', '#dc3545'),
('mantenimiento', 'Habitación en reparación o mantenimiento', '#ffc107'),
('reservada', 'Habitación reservada para futura llegada', '#17a2b8'),
('limpieza', 'Habitación en proceso de limpieza', '#6c757d');

-- Características de habitación
INSERT INTO caracteristicas_habitacion (nombre, icono) VALUES
('Aire acondicionado', '❄️'),
('WiFi gratuito', '📶'),
('TV por cable', '📺'),
('Minibar', '🥤'),
('Caja fuerte', '🔒'),
('Bañera', '🛁'),
('Vista al mar', '🌊'),
('Balcón', '🏞️'),
('Hidromasaje', '💆'),
('Escritorio', '💼');

-- Temporadas
INSERT INTO temporadas (nombre, fecha_inicio, fecha_fin, factor_multipliador) VALUES
('Temporada Baja', '2024-01-10', '2024-03-31', 0.85),
('Temporada Media', '2024-04-01', '2024-06-14', 1.0),
('Temporada Alta', '2024-06-15', '2024-09-15', 1.35),
('Temporada Media', '2024-09-16', '2024-12-20', 1.0),
('Temporada Alta (Navidad)', '2024-12-21', '2025-01-07', 1.5),
('Temporada Baja', '2025-01-08', '2025-03-31', 0.85),
('Temporada Media', '2025-04-01', '2025-12-31', 1.0);

-- Servicios adicionales
INSERT INTO servicios (nombre, descripcion, precio_base, categoria) VALUES
('Desayuno buffet', 'Desayuno buffet completo', 15.00, 'restaurante'),
('Almuerzo', 'Menú del día', 25.00, 'restaurante'),
('Cena', 'Cena a la carta', 35.00, 'restaurante'),
('Lavandería', 'Servicio de lavado y planchado por prenda', 8.00, 'lavandería'),
('Spa - Masaje', 'Masaje relajante de 60 minutos', 60.00, 'spa'),
('Minibar - Agua', 'Botella de agua', 3.00, 'minibar'),
('Minibar - Refresco', 'Lata de refresco', 4.00, 'minibar'),
('Minibar - Cerveza', 'Botella de cerveza', 5.00, 'minibar'),
('Gimnasio', 'Acceso al gimnasio', 10.00, 'spa'),
('Parking', 'Estacionamiento por día', 12.00, 'servicio');

-- =====================================================
-- 🏨 2. HABITACIONES (DEPENDEN DE TIPOS Y ESTADOS)
-- =====================================================

-- Habitaciones de ejemplo
INSERT INTO habitaciones (numero, piso, tipo_habitacion_id, tarifa_base, tiene_vista, metros_cuadrados) VALUES
('101', 1, 1, 85.00, false, 18.5),
('102', 1, 1, 85.00, false, 18.5),
('103', 1, 2, 120.00, false, 25.0),
('104', 1, 2, 120.00, true, 25.0),
('201', 2, 2, 135.00, true, 28.0),
('202', 2, 2, 135.00, false, 28.0),
('301', 3, 3, 250.00, true, 45.0),
('302', 3, 3, 250.00, true, 45.0),
('401', 4, 4, 350.00, true, 65.0),
('501', 5, 5, 500.00, true, 95.0);

-- =====================================================
-- 🔗 3. RELACIONES (HABITACIONES - CARACTERÍSTICAS)
-- =====================================================

-- Asignar características a habitaciones
INSERT INTO habitacion_caracteristicas (habitacion_id, caracteristica_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 5),
(2, 1), (2, 2), (2, 3), (2, 5),
(3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6),
(4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7),
(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9);

-- =====================================================
-- 👥 4. USUARIOS
-- =====================================================

INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol) VALUES
('admin', '$2b$12$CufCza2ZDhoS2BnRMG2.a.Yj39CgQxPug7ea8hyPuzK8a1HVk6ng2', 'Administrador', 'admin@hotel.com', 'admin'),
('gerente', '$2b$12$CufCza2ZDhoS2BnRMG2.a.Yj39CgQxPug7ea8hyPuzK8a1HVk6ng2', 'Gerente General', 'gerente@hotel.com', 'gerente'),
('recepcion1', '$2b$12$CufCza2ZDhoS2BnRMG2.a.Yj39CgQxPug7ea8hyPuzK8a1HVk6ng2', 'Juan Pérez', 'juan.perez@hotel.com', 'recepcionista');

-- =====================================================
-- 👥 5. HUÉSPEDES
-- =====================================================

INSERT INTO huespedes (nombre, apellido, tipo_documento, numero_documento, email, telefono, nacionalidad, es_vip, fecha_nacimiento, direccion, ciudad, pais) VALUES
-- Peruanos (8)
('Juan', 'Pérez', 'DNI', '12345678', 'juan.perez@gmail.com', '987654321', 'Peruana', false, '1985-03-15', 'Av. Arequipa 123', 'Lima', 'Perú'),
('María', 'González', 'DNI', '87654321', 'maria.gonzalez@gmail.com', '987654322', 'Peruana', true, '1990-07-22', 'Calle Las Flores 456', 'Arequipa', 'Perú'),
('Carlos', 'Rodríguez', 'DNI', '45678912', 'carlos.rodriguez@hotmail.com', '987654323', 'Peruana', false, '1978-11-30', 'Av. Larco 789', 'Trujillo', 'Perú'),
('Ana', 'Martínez', 'DNI', '32165498', 'ana.martinez@yahoo.com', '987654324', 'Peruana', false, '1982-09-18', 'Jr. Unión 234', 'Cusco', 'Perú'),
('Roberto', 'Sánchez', 'DNI', '65498732', 'roberto.sanchez@gmail.com', '987654325', 'Peruana', true, '1975-05-10', 'Av. Brasil 567', 'Lima', 'Perú'),
('Laura', 'Fernández', 'DNI', '15975346', 'laura.fernandez@hotmail.com', '987654326', 'Peruana', false, '1995-12-05', 'Calle Los Pinos 890', 'Piura', 'Perú'),
('Diego', 'López', 'DNI', '75395182', 'diego.lopez@gmail.com', '987654327', 'Peruana', false, '1988-04-25', 'Av. Grau 1234', 'Chiclayo', 'Perú'),
('Carmen', 'Díaz', 'DNI', '85296374', 'carmen.diaz@yahoo.com', '987654328', 'Peruana', true, '1980-08-12', 'Jr. Amazonas 567', 'Iquitos', 'Perú'),

-- Argentinos (3)
('Javier', 'Torres', 'Pasaporte', 'ARG123456', 'javier.torres@gmail.com', '54123456789', 'Argentina', false, '1976-06-20', 'Av. Corrientes 2345', 'Buenos Aires', 'Argentina'),
('Patricia', 'Ruiz', 'Pasaporte', 'ARG789012', 'patricia.ruiz@hotmail.com', '54123456790', 'Argentina', true, '1983-02-14', 'Calle Florida 678', 'Buenos Aires', 'Argentina'),
('Gustavo', 'Morales', 'Pasaporte', 'ARG345678', 'gustavo.morales@gmail.com', '54123456791', 'Argentina', false, '1970-09-08', 'Av. Santa Fe 901', 'Córdoba', 'Argentina'),

-- Chilenos (3)
('Fernanda', 'Silva', 'Pasaporte', 'CHI123456', 'fernanda.silva@gmail.com', '56912345678', 'Chilena', false, '1987-11-11', 'Av. Providencia 1234', 'Santiago', 'Chile'),
('Rodrigo', 'Muñoz', 'Pasaporte', 'CHI789012', 'rodrigo.munoz@hotmail.com', '56912345679', 'Chilena', true, '1979-03-27', 'Calle Los Leones 567', 'Valparaíso', 'Chile'),
('Carolina', 'Rojas', 'Pasaporte', 'CHI345678', 'carolina.rojas@gmail.com', '56912345680', 'Chilena', false, '1992-07-19', 'Av. Kennedy 890', 'Concepción', 'Chile'),

-- Españoles (3)
('Alejandro', 'García', 'Pasaporte', 'ESP123456', 'alejandro.garcia@gmail.com', '34912345678', 'Española', true, '1984-10-05', 'Gran Vía 123', 'Madrid', 'España'),
('Marta', 'López', 'Pasaporte', 'ESP789012', 'marta.lopez@hotmail.com', '34912345679', 'Española', false, '1991-01-30', 'La Rambla 456', 'Barcelona', 'España'),
('David', 'Martínez', 'Pasaporte', 'ESP345678', 'david.martinez@gmail.com', '34912345680', 'Española', false, '1977-12-12', 'Plaza Mayor 789', 'Sevilla', 'España'),

-- Mexicanos (3)
('Sofía', 'Hernández', 'Pasaporte', 'MEX123456', 'sofia.hernandez@gmail.com', '52123456789', 'Mexicana', true, '1986-05-25', 'Paseo de la Reforma 123', 'CDMX', 'México'),
('Luis', 'Ramírez', 'Pasaporte', 'MEX789012', 'luis.ramirez@hotmail.com', '52123456790', 'Mexicana', false, '1981-08-15', 'Av. Insurgentes 456', 'Guadalajara', 'México'),
('Diana', 'Flores', 'Pasaporte', 'MEX345678', 'diana.flores@gmail.com', '52123456791', 'Mexicana', false, '1993-03-08', 'Calle Madero 789', 'Monterrey', 'México');

-- =====================================================
-- 📅 6. RESERVAS
-- =====================================================

-- RESERVAS ACTIVAS PARA HOY (3)
INSERT INTO reservas (huesped_id, fecha_reserva, fecha_check_in, fecha_check_out, 
                     numero_adultos, numero_ninos, estado, habitacion_id, tarifa_total, notas, created_by)
VALUES
(1, CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE, CURRENT_DATE + INTERVAL '3 days', 2, 0, 'confirmada', 1, 350.00, 'Solicitó habitación tranquila', 3),
(2, CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days', 2, 1, 'confirmada', 2, 280.00, 'Con bebé de 1 año', 3),
(3, CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE, CURRENT_DATE + INTERVAL '4 days', 1, 0, 'confirmada', 3, 420.00, 'Viajero de negocios', 3);

-- RESERVAS PARA MAÑANA (3)
INSERT INTO reservas (huesped_id, fecha_reserva, fecha_check_in, fecha_check_out, 
                     numero_adultos, numero_ninos, estado, habitacion_id, tarifa_total, notas, created_by)
VALUES
(4, CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE + INTERVAL '1 day', CURRENT_DATE + INTERVAL '4 days', 2, 2, 'confirmada', 4, 550.00, 'Familia con 2 niños', 3),
(5, CURRENT_DATE - INTERVAL '4 days', CURRENT_DATE + INTERVAL '1 day', CURRENT_DATE + INTERVAL '3 days', 2, 0, 'confirmada', 5, 390.00, 'Huésped VIP', 2),
(6, CURRENT_DATE - INTERVAL '6 days', CURRENT_DATE + INTERVAL '1 day', CURRENT_DATE + INTERVAL '5 days', 2, 0, 'confirmada', 6, 420.00, NULL, 3);

-- RESERVAS PASADAS (4)
INSERT INTO reservas (huesped_id, fecha_reserva, fecha_check_in, fecha_check_out, 
                     numero_adultos, numero_ninos, estado, habitacion_id, tarifa_total, notas, created_by)
VALUES
(7, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE + INTERVAL '1 day', 2, 0, 'confirmada', 7, 650.00, 'Solicitó cama adicional', 3),
(8, CURRENT_DATE - INTERVAL '12 days', CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE, 2, 0, 'confirmada', 8, 750.00, 'Huésped VIP', 2),
(9, CURRENT_DATE - INTERVAL '15 days', CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE - INTERVAL '1 day', 2, 0, 'completada', 9, 1250.00, 'Suite presidencial', 2),
(10, CURRENT_DATE - INTERVAL '14 days', CURRENT_DATE - INTERVAL '4 days', CURRENT_DATE - INTERVAL '1 day', 2, 1, 'completada', 10, 1800.00, 'Con niño pequeño', 2);

-- RESERVAS FUTURAS (10)
INSERT INTO reservas (huesped_id, fecha_reserva, fecha_check_in, fecha_check_out, 
                     numero_adultos, numero_ninos, estado, habitacion_id, tarifa_total, notas, created_by)
VALUES
(11, CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE + INTERVAL '7 days', CURRENT_DATE + INTERVAL '10 days', 2, 0, 'confirmada', 1, 380.00, NULL, 2),
(12, CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE + INTERVAL '8 days', CURRENT_DATE + INTERVAL '12 days', 2, 0, 'confirmada', 2, 420.00, 'Solicitó habitación con vista', 3),
(13, CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE + INTERVAL '10 days', CURRENT_DATE + INTERVAL '14 days', 2, 0, 'confirmada', 3, 520.00, 'Huésped VIP', 2),
(14, CURRENT_DATE - INTERVAL '8 days', CURRENT_DATE + INTERVAL '12 days', CURRENT_DATE + INTERVAL '15 days', 2, 2, 'confirmada', 4, 480.00, 'Familia con 2 niños', 3),
(15, CURRENT_DATE - INTERVAL '6 days', CURRENT_DATE + INTERVAL '15 days', CURRENT_DATE + INTERVAL '18 days', 1, 0, 'confirmada', 5, 420.00, 'Viajero de negocios', 2),
(16, CURRENT_DATE - INTERVAL '9 days', CURRENT_DATE + INTERVAL '18 days', CURRENT_DATE + INTERVAL '22 days', 2, 0, 'confirmada', 6, 540.00, 'Luna de miel', 3),
(17, CURRENT_DATE - INTERVAL '4 days', CURRENT_DATE + INTERVAL '20 days', CURRENT_DATE + INTERVAL '25 days', 2, 0, 'confirmada', 7, 980.00, NULL, 2),
(18, CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE + INTERVAL '22 days', CURRENT_DATE + INTERVAL '27 days', 2, 1, 'confirmada', 8, 1050.00, 'Huésped VIP', 2),
(19, CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE + INTERVAL '25 days', CURRENT_DATE + INTERVAL '30 days', 2, 0, 'confirmada', 9, 1650.00, 'Suite de lujo', 3),
(20, CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE + INTERVAL '28 days', CURRENT_DATE + INTERVAL '32 days', 2, 0, 'confirmada', 10, 2350.00, 'Presidencial', 2);

-- RESERVAS CANCELADAS (5)
INSERT INTO reservas (huesped_id, fecha_reserva, fecha_check_in, fecha_check_out, 
                     numero_adultos, numero_ninos, estado, habitacion_id, tarifa_total, 
                     fecha_cancelacion, motivo_cancelacion)
VALUES
(1, CURRENT_DATE - INTERVAL '20 days', CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE - INTERVAL '7 days', 2, 0, 'cancelada', 1, 320.00, CURRENT_DATE - INTERVAL '13 days', 'Cambio de planes'),
(2, CURRENT_DATE - INTERVAL '18 days', CURRENT_DATE - INTERVAL '8 days', CURRENT_DATE - INTERVAL '5 days', 2, 1, 'cancelada', 2, 280.00, CURRENT_DATE - INTERVAL '10 days', 'Emergencia familiar'),
(3, CURRENT_DATE - INTERVAL '15 days', CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE - INTERVAL '2 days', 1, 0, 'no_show', 3, 210.00, NULL, NULL),
(4, CURRENT_DATE - INTERVAL '12 days', CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE + INTERVAL '1 day', 2, 2, 'cancelada', 4, 480.00, CURRENT_DATE - INTERVAL '5 days', 'Cancelación con reembolso'),
(5, CURRENT_DATE - INTERVAL '25 days', CURRENT_DATE + INTERVAL '5 days', CURRENT_DATE + INTERVAL '8 days', 2, 0, 'cancelada', 5, 360.00, CURRENT_DATE - INTERVAL '10 days', 'Cambio de destino');

-- =====================================================
-- 🏨 7. ALOJAMIENTOS
-- =====================================================

INSERT INTO alojamientos (reserva_id, habitacion_asignada_id, fecha_check_in, 
                         llave_entregada, usuario_check_in, observaciones_check_in)
SELECT r.id, r.habitacion_id, 
       CASE 
           WHEN r.id = 3 THEN CURRENT_TIMESTAMP - INTERVAL '3 hours'
           WHEN r.id = 7 THEN r.fecha_check_in::timestamp + INTERVAL '15 hours'
           WHEN r.id = 8 THEN r.fecha_check_in::timestamp + INTERVAL '14 hours'
           WHEN r.id = 9 THEN r.fecha_check_in::timestamp + INTERVAL '16 hours'
           WHEN r.id = 10 THEN r.fecha_check_in::timestamp + INTERVAL '13 hours'
       END,
       true, 3,
       CASE 
           WHEN r.id = 3 THEN 'Check-in normal'
           WHEN r.id = 7 THEN 'Check-in sin problemas'
           WHEN r.id = 8 THEN 'Huésped VIP'
           WHEN r.id = 9 THEN 'Check-in suite'
           WHEN r.id = 10 THEN 'Familia con niño'
       END
FROM reservas r 
WHERE r.id IN (3, 7, 8, 9, 10);

-- Actualizar fechas de check-out para alojamientos completados
UPDATE alojamientos 
SET fecha_check_out = r.fecha_check_out::timestamp + INTERVAL '11 hours',
    llave_devuelta = true,
    usuario_check_out = 2
FROM reservas r
WHERE alojamientos.reserva_id = r.id AND r.id IN (9, 10);

-- =====================================================
-- 🧾 8. FACTURAS
-- =====================================================

CREATE SEQUENCE IF NOT EXISTS facturas_numero_seq;

INSERT INTO facturas (numero_factura, huesped_id, reserva_id, fecha_emision, 
                     subtotal, impuestos, total, estado, metodo_pago, fecha_pago)
SELECT 'FAC-2026-001', 9, 9, r.fecha_check_out, 1250.00, 225.00, 1475.00, 'pagada', 'tarjeta', r.fecha_check_out + INTERVAL '2 hours'
FROM reservas r WHERE r.id = 9
UNION ALL
SELECT 'FAC-2026-002', 10, 10, r.fecha_check_out, 1800.00, 324.00, 2124.00, 'pagada', 'efectivo', r.fecha_check_out + INTERVAL '1 hour'
FROM reservas r WHERE r.id = 10;

-- Detalle facturas
INSERT INTO detalle_factura (factura_id, concepto, cantidad, precio_unitario, importe, tipo)
VALUES 
(1, 'Alojamiento - Suite 5 noches', 1, 1250.00, 1250.00, 'alojamiento'),
(1, 'Desayuno buffet', 5, 25.00, 125.00, 'restaurante'),
(1, 'Cena especial', 2, 45.00, 90.00, 'restaurante'),
(2, 'Alojamiento - Presidencial 4 noches', 1, 1800.00, 1800.00, 'alojamiento'),
(2, 'Servicio de lavandería', 3, 12.00, 36.00, 'servicio'),
(2, 'Minibar', 2, 25.00, 50.00, 'minibar'),
(2, 'Cena restaurante', 2, 35.00, 70.00, 'restaurante');

-- =====================================================
-- 🍽️ 9. CONSUMOS
-- =====================================================

INSERT INTO consumos_servicios (alojamiento_id, servicio_id, cantidad, precio_unitario, notas)
VALUES 
(2, 1, 2, 15.00, 'Desayuno - Día 1'),
(2, 1, 2, 15.00, 'Desayuno - Día 2'),
(2, 6, 3, 3.00, 'Agua mineral'),
(2, 7, 2, 4.00, 'Refrescos'),
(3, 1, 2, 15.00, 'Desayuno - Día 1'),
(3, 1, 2, 15.00, 'Desayuno - Día 2'),
(3, 1, 2, 15.00, 'Desayuno - Día 3'),
(3, 5, 1, 60.00, 'Masaje relajante'),
(3, 9, 2, 10.00, 'Acceso gimnasio');

-- =====================================================
-- 🏷️ 10. ACTUALIZACIONES FINALES
-- =====================================================

-- Actualizar estados de habitaciones
UPDATE habitaciones SET estado_id = 2 WHERE id IN (3, 7, 8); -- 103, 301, 302 ocupadas

-- =====================================================
-- 📊 VERIFICACIÓN FINAL
-- =====================================================

SELECT '========================================' as info;
SELECT '🌟 SISTEMA HOTELERO - CARGA COMPLETA 🌟' as info;
SELECT '========================================' as info;

SELECT '📊 RESUMEN DE DATOS CARGADOS:' as info;

SELECT 
    '👥 Huéspedes' as tabla, 
    COUNT(*) as total
FROM huespedes
UNION ALL
SELECT 
    '📅 Reservas', 
    COUNT(*)
FROM reservas
UNION ALL
SELECT 
    '🏨 Alojamientos', 
    COUNT(*)
FROM alojamientos
UNION ALL
SELECT 
    '🧾 Facturas', 
    COUNT(*)
FROM facturas
UNION ALL
SELECT 
    '🍽️ Consumos', 
    COUNT(*)
FROM consumos_servicios;