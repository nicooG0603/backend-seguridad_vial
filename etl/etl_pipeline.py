import os
import csv
import sqlite3
import datetime
from datetime import datetime as dt
import mysql.connector

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'etl', 'datos_crudos.csv')
SQLITE_DB_PATH = os.path.join(BASE_DIR, 'database', 'dwh.db')

import dotenv
dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Configuración de base de datos MySQL (por defecto intenta MySQL, cae en SQLite si falla)
MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'dwh_seguridad_vial')
}


def normalizar_bloque(hora_inicio):
    """Mapea una hora de inicio de 15 min al bloque correspondiente de 2 horas."""
    try:
        partes = hora_inicio.split(':')
        hora = int(partes[0])
        if 6 <= hora < 12:
            return 'Mañana (07:00-09:00)'
        elif 12 <= hora < 17:
            return 'Tarde (12:00-14:00)'
        else:
            return 'Tarde-Noche (17:00-19:00)'
    except Exception:
        return 'Inválido'

def procesar_etl():
    """Ejecuta el pipeline ETL desde el CSV crudo."""
    print("Iniciando Pipeline ETL...")
    inicio = dt.now()
    total_procesados = 0
    registros_cargados = 0
    registros_error = 0
    
    # 1. Leer datos crudos desde el CSV
    try:
        with open(CSV_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            filas = list(reader)
    except Exception as e:
        print(f"Error al abrir el archivo CSV: {e}")
        return False

    # 2. Conectar a la Base de Datos (Primero MySQL, si no SQLite)
    use_mysql = False
    conn = None
    cursor = None
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        use_mysql = True
        print("Conectado con éxito a MySQL. Cargando DWH...")
    except Exception as e:
        print(f"No se pudo conectar a MySQL: {e}.")
        print("Usando base de datos fallback local SQLite...")
        # Configurar base de datos SQLite local
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Crear tablas en SQLite en caso de que no existan
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS dim_intersecciones (
                id_interseccion INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_interseccion TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS dim_tiempo (
                id_tiempo INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                hora_inicio TEXT NOT NULL,
                hora_fin TEXT NOT NULL,
                bloque_horario TEXT NOT NULL,
                UNIQUE (fecha, hora_inicio, hora_fin)
            );
            CREATE TABLE IF NOT EXISTS fact_observaciones (
                id_observacion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_interseccion INTEGER NOT NULL,
                id_tiempo INTEGER NOT NULL,
                vehiculos_contados INTEGER NOT NULL,
                peatones_contados INTEGER NOT NULL,
                infracciones_cinturon INTEGER NOT NULL,
                infracciones_celular INTEGER NOT NULL,
                infracciones_senaletica INTEGER NOT NULL,
                infracciones_giro INTEGER NOT NULL,
                total_infracciones INTEGER NOT NULL,
                indice_riesgo REAL NOT NULL,
                fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_interseccion) REFERENCES dim_intersecciones(id_interseccion),
                FOREIGN KEY (id_tiempo) REFERENCES dim_tiempo(id_tiempo)
            );
            CREATE TABLE IF NOT EXISTS log_etl (
                id_log INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_inicio TEXT NOT NULL,
                timestamp_fin TEXT,
                duracion_segundos INTEGER,
                total_procesados INTEGER DEFAULT 0,
                registros_cargados INTEGER DEFAULT 0,
                registros_error INTEGER DEFAULT 0,
                estado TEXT DEFAULT 'exitoso',
                mensaje_error TEXT
            );
        """)
        conn.commit()

    # 3. Limpiar y Transformar
    for fila in filas:
        total_procesados += 1
        try:
            interseccion = fila['interseccion'].strip()
            fecha = fila['fecha'].strip()
            hora_inicio = fila['hora_inicio'].strip()
            hora_fin = fila['hora_fin'].strip()
            vehiculos = int(fila['vehiculos_contados'])
            peatones = int(fila['peatones_contados'])
            cinturon = int(fila['infracciones_cinturon'])
            celular = int(fila['infracciones_celular'])
            senaletica_infr = int(fila['infracciones_senaletica'])
            giro = int(fila['infracciones_giro'])
            
            # Validación simple de rangos
            if vehiculos <= 0 or peatones < 0 or cinturon < 0 or celular < 0 or senaletica_infr < 0 or giro < 0:
                raise ValueError("Valores numéricos no pueden ser negativos ni cero vehículos.")
                
            # Normalizar bloque horario
            bloque = normalizar_bloque(hora_inicio)
            if bloque in ['Fuera de Rango', 'Inválido']:
                raise ValueError(f"Bloque horario fuera de rango o inválido para hora: {hora_inicio}")
                
            # Cálculos de negocio
            total_infracciones = cinturon + celular + senaletica_infr + giro
            indice_riesgo = round((total_infracciones / vehiculos) * 100, 2)
            
            # --- CARGA (Cargar dimensiones y hechos) ---
            
            # Cargar Dimensión Intersección
            if use_mysql:
                cursor.execute("""
                    INSERT INTO dim_intersecciones (nombre_interseccion) 
                    VALUES (%s) 
                    ON DUPLICATE KEY UPDATE nombre_interseccion=VALUES(nombre_interseccion)
                """, (interseccion,))
                cursor.execute("SELECT id_interseccion FROM dim_intersecciones WHERE nombre_interseccion = %s", (interseccion,))
                id_interseccion = cursor.fetchone()['id_interseccion']
            else:
                cursor.execute("""
                    INSERT OR IGNORE INTO dim_intersecciones (nombre_interseccion) 
                    VALUES (?)
                """, (interseccion,))
                cursor.execute("SELECT id_interseccion FROM dim_intersecciones WHERE nombre_interseccion = ?", (interseccion,))
                id_interseccion = cursor.fetchone()[0]

            # Cargar Dimensión Tiempo
            if use_mysql:
                cursor.execute("""
                    INSERT INTO dim_tiempo (fecha, hora_inicio, hora_fin, bloque_horario)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE bloque_horario=VALUES(bloque_horario)
                """, (fecha, hora_inicio, hora_fin, bloque))
                cursor.execute("""
                    SELECT id_tiempo FROM dim_tiempo 
                    WHERE fecha = %s AND hora_inicio = %s AND hora_fin = %s
                """, (fecha, hora_inicio, hora_fin))
                id_tiempo = cursor.fetchone()['id_tiempo']
            else:
                cursor.execute("""
                    INSERT OR IGNORE INTO dim_tiempo (fecha, hora_inicio, hora_fin, bloque_horario)
                    VALUES (?, ?, ?, ?)
                """, (fecha, hora_inicio, hora_fin, bloque))
                cursor.execute("""
                    SELECT id_tiempo FROM dim_tiempo 
                    WHERE fecha = ? AND hora_inicio = ? AND hora_fin = ?
                """, (fecha, hora_inicio, hora_fin))
                id_tiempo = cursor.fetchone()[0]

            # Insertar en Fact de hechos (Deduplicar por interseccion + tiempo para cumplir SLA 100% de unicidad)
            if use_mysql:
                # Comprobar si ya existe una observación para esta intersección y tiempo
                cursor.execute("""
                    SELECT id_observacion FROM fact_observaciones 
                    WHERE id_interseccion = %s AND id_tiempo = %s
                """, (id_interseccion, id_tiempo))
                existente = cursor.fetchone()
                
                if existente:
                    # Actualizar
                    cursor.execute("""
                        UPDATE fact_observaciones SET 
                            vehiculos_contados = %s, peatones_contados = %s, 
                            infracciones_cinturon = %s, infracciones_celular = %s, infracciones_senaletica = %s, 
                            infracciones_giro = %s, total_infracciones = %s, indice_riesgo = %s
                        WHERE id_observacion = %s
                    """, (vehiculos, peatones, cinturon, celular, senaletica_infr, giro, total_infracciones, indice_riesgo, existente['id_observacion']))
                else:
                    # Insertar nuevo
                    cursor.execute("""
                        INSERT INTO fact_observaciones (id_interseccion, id_tiempo, vehiculos_contados, peatones_contados, infracciones_cinturon, infracciones_celular, infracciones_senaletica, infracciones_giro, total_infracciones, indice_riesgo)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (id_interseccion, id_tiempo, vehiculos, peatones, cinturon, celular, senaletica_infr, giro, total_infracciones, indice_riesgo))
            else:
                # SQLite
                cursor.execute("""
                    SELECT id_observacion FROM fact_observaciones 
                    WHERE id_interseccion = ? AND id_tiempo = ?
                """, (id_interseccion, id_tiempo))
                existente = cursor.fetchone()
                
                if existente:
                    cursor.execute("""
                        UPDATE fact_observaciones SET 
                            vehiculos_contados = ?, peatones_contados = ?, 
                            infracciones_cinturon = ?, infracciones_celular = ?, infracciones_senaletica = ?, 
                            infracciones_giro = ?, total_infracciones = ?, indice_riesgo = ?
                        WHERE id_observacion = ?
                    """, (vehiculos, peatones, cinturon, celular, senaletica_infr, giro, total_infracciones, indice_riesgo, existente[0]))
                else:
                    cursor.execute("""
                        INSERT INTO fact_observaciones (id_interseccion, id_tiempo, vehiculos_contados, peatones_contados, infracciones_cinturon, infracciones_celular, infracciones_senaletica, infracciones_giro, total_infracciones, indice_riesgo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (id_interseccion, id_tiempo, vehiculos, peatones, cinturon, celular, senaletica_infr, giro, total_infracciones, indice_riesgo))

            registros_cargados += 1
        except Exception as e:
            print(f"Error procesando fila {total_procesados}: {e}")
            registros_error += 1

    # 4. Finalizar y guardar Auditoría
    fin = dt.now()
    duracion = int((fin - inicio).total_seconds())
    estado_final = "exitoso" if registros_error == 0 else "parcial"
    
    if use_mysql:
        cursor.execute("""
            INSERT INTO log_etl (timestamp_inicio, timestamp_fin, duracion_segundos, total_procesados, registros_cargados, registros_error, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (inicio, fin, duracion, total_procesados, registros_cargados, registros_error, estado_final))
    else:
        cursor.execute("""
            INSERT INTO log_etl (timestamp_inicio, timestamp_fin, duracion_segundos, total_procesados, registros_cargados, registros_error, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (inicio.isoformat(), fin.isoformat(), duracion, total_procesados, registros_cargados, registros_error, estado_final))

    conn.commit()
    conn.close()
    
    print(f"ETL finalizado en {duracion}s. Procesados: {total_procesados}, Cargados: {registros_cargados}, Errores: {registros_error}.")
    return True

if __name__ == '__main__':
    procesar_etl()
