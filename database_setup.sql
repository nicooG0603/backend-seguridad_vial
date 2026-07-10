-- ==========================================
-- ESTRUCTURA DE LA BASE DE DATOS
-- ==========================================

CREATE DATABASE IF NOT EXISTS seguridad_vial;
USE seguridad_vial;

-- 1. Tabla dimensional de Intersecciones
CREATE TABLE IF NOT EXISTS dim_interseccion (
    id_interseccion INT AUTO_INCREMENT PRIMARY KEY,
    nombre_interseccion VARCHAR(255) UNIQUE NOT NULL,
    calle_principal VARCHAR(150) NOT NULL,
    calle_secundaria VARCHAR(150) NOT NULL
);

-- 2. Tabla de hechos de Observaciones Viales
CREATE TABLE IF NOT EXISTS fact_observacion_vial (
    id_observacion INT AUTO_INCREMENT PRIMARY KEY,
    id_interseccion INT,
    fecha_observacion DATE NOT NULL,
    franja_horaria VARCHAR(50) NOT NULL,
    vehiculos_15min INT NOT NULL,
    peatones_15min INT NOT NULL,
    infraccion_cinturon INT NOT NULL,
    infraccion_celular INT NOT NULL,
    infraccion_senaletica INT NOT NULL,
    infraccion_giro INT NOT NULL,
    total_infracciones INT NOT NULL,
    indice_riesgo DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (id_interseccion) REFERENCES dim_interseccion(id_interseccion)
);

-- ==========================================
-- DATOS DE PRUEBA (SEMILLA)
-- ==========================================

-- Limpiar datos previos si existen (cuidado si se corre en prod)
-- DELETE FROM fact_observacion_vial;
-- DELETE FROM dim_interseccion;

-- Insertar intersecciones de ejemplo
INSERT INTO dim_interseccion (id_interseccion, nombre_interseccion, calle_principal, calle_secundaria) VALUES
(1, 'Av. Libertador y Av. Callao', 'Av. del Libertador', 'Av. Callao'),
(2, 'Av. 9 de Julio y Av. Corrientes', 'Av. 9 de Julio', 'Av. Corrientes'),
(3, 'Av. Santa Fe y Av. Pueyrredón', 'Av. Santa Fe', 'Av. Pueyrredón'),
(4, 'Av. Rivadavia y Av. Acoyte', 'Av. Rivadavia', 'Av. Acoyte')
ON DUPLICATE KEY UPDATE nombre_interseccion=VALUES(nombre_interseccion);

-- Insertar observaciones viales de ejemplo
INSERT INTO fact_observacion_vial 
(id_interseccion, fecha_observacion, franja_horaria, vehiculos_15min, peatones_15min, infraccion_cinturon, infraccion_celular, infraccion_senaletica, infraccion_giro, total_infracciones, indice_riesgo)
VALUES
-- Intersección 1 (Libertador y Callao) - Riesgo moderado-alto
(1, '2026-07-10', 'Mañana', 350, 120, 5, 8, 3, 2, 18, 4.20),
(1, '2026-07-10', 'Mediodía', 420, 180, 4, 12, 1, 4, 21, 5.10),
(1, '2026-07-10', 'Tarde', 480, 220, 8, 15, 6, 3, 32, 6.80),

-- Intersección 2 (9 de Julio y Corrientes) - Riesgo muy alto
(2, '2026-07-10', 'Mañana', 600, 300, 15, 20, 12, 8, 55, 8.50),
(2, '2026-07-10', 'Mediodía', 550, 350, 10, 18, 8, 5, 41, 7.90),
(2, '2026-07-10', 'Tarde', 700, 400, 18, 25, 15, 10, 68, 9.20),

-- Intersección 3 (Santa Fe y Pueyrredón) - Riesgo moderado
(3, '2026-07-10', 'Mañana', 280, 150, 3, 5, 2, 1, 11, 2.90),
(3, '2026-07-10', 'Mediodía', 310, 200, 2, 6, 4, 3, 15, 3.40),
(3, '2026-07-10', 'Tarde', 340, 210, 4, 9, 3, 2, 18, 3.80),

-- Intersección 4 (Rivadavia y Acoyte) - Riesgo medio-alto
(4, '2026-07-10', 'Mañana', 390, 160, 6, 11, 4, 2, 23, 4.90),
(4, '2026-07-10', 'Mediodía', 410, 190, 5, 13, 3, 4, 25, 5.30),
(4, '2026-07-10', 'Tarde', 460, 250, 9, 14, 5, 3, 31, 6.10);
