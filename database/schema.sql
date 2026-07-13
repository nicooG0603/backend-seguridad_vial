-- Script de creación de Base de Datos y Estructura Dimensional (DWH)
-- Proyecto: Dashboard de Seguridad Vial Urbana (Proyecto 5)
-- Sprint: 1

-- Creación de la base de datos si no existe
CREATE DATABASE IF NOT EXISTS dwh_seguridad_vial;
USE dwh_seguridad_vial;

-- 1. Dimensión de Intersecciones (Sin columna Zona)
CREATE TABLE IF NOT EXISTS dim_intersecciones (
    id_interseccion INT AUTO_INCREMENT PRIMARY KEY,
    nombre_interseccion VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Dimensión de Tiempo
CREATE TABLE IF NOT EXISTS dim_tiempo (
    id_tiempo INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    hora_inicio VARCHAR(5) NOT NULL,
    hora_fin VARCHAR(5) NOT NULL,
    bloque_horario VARCHAR(50) NOT NULL,
    CONSTRAINT unique_tiempo UNIQUE (fecha, hora_inicio, hora_fin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Tabla de Hechos de Observaciones (Sin id_senaletica)
CREATE TABLE IF NOT EXISTS fact_observaciones (
    id_observacion INT AUTO_INCREMENT PRIMARY KEY,
    id_interseccion INT NOT NULL,
    id_tiempo INT NOT NULL,
    vehiculos_contados INT NOT NULL,
    peatones_contados INT NOT NULL,
    infracciones_cinturon INT NOT NULL,
    infracciones_celular INT NOT NULL,
    infracciones_senaletica INT NOT NULL,
    infracciones_giro INT NOT NULL,
    total_infracciones INT NOT NULL,
    indice_riesgo DECIMAL(5,2) NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_interseccion) REFERENCES dim_intersecciones(id_interseccion) ON DELETE CASCADE,
    FOREIGN KEY (id_tiempo) REFERENCES dim_tiempo(id_tiempo) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Tabla de Log de Auditoría ETL (Requerida para SLAs de Latencia y Error Rate)
CREATE TABLE IF NOT EXISTS log_etl (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    timestamp_inicio DATETIME NOT NULL,
    timestamp_fin DATETIME,
    duracion_segundos INT,
    total_procesados INT DEFAULT 0,
    registros_cargados INT DEFAULT 0,
    registros_error INT DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'exitoso',
    mensaje_error VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Población inicial para dimensiones estáticas
-- ============================================================================

-- Poblar Intersecciones sugeridas (≥ 5 requeridas para el proyecto)
INSERT IGNORE INTO dim_intersecciones (nombre_interseccion) VALUES
('14 la fama / Eduardo Frei Montalva'),
('AV Dorsal / Bravo de Sarabia'),
('Av Balmaceda / Aníbal Montt'),
('Av Dorsal / AV PDTE EDUARDO FREI MONTALVA'),
('Av Dorsal / Av Domingo Santa Maria'),
('Av Dorsal / Anibal Montt');
