import os
import sqlite3
import datetime
from datetime import datetime as dt
from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

import dotenv
dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)  # Habilitar CORS para que el dashboard pueda comunicarse con la API

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = os.path.join(BASE_DIR, 'database', 'dwh.db')

# Configuración de base de datos MySQL
MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'dwh_seguridad_vial')
}


def get_db_connection():
    """Intenta conectar a MySQL y cae en SQLite en caso de error."""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn, True
    except Exception:
        # Fallback a SQLite
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn, False

def inicializar_datos_si_vacio():
    """Verifica si la base de datos está vacía e importa datos iniciales si es necesario."""
    conn, is_mysql = get_db_connection()
    cursor = conn.cursor(dictionary=True) if is_mysql else conn.cursor()
    
    try:
        # Comprobar si hay registros en la tabla de hechos
        if is_mysql:
            cursor.execute("SELECT COUNT(*) as total FROM fact_observaciones")
            total = cursor.fetchone()['total']
        else:
            cursor.execute("SELECT COUNT(*) FROM fact_observaciones")
            total = cursor.fetchone()[0]
            
        if total == 0:
            print("Base de datos vacía detectada al inicio. Ejecutando ETL pipeline...")
            from etl.etl_pipeline import procesar_etl
            procesar_etl()
    except Exception as e:
        print(f"Error al verificar o inicializar base de datos: {e}")
        # Intentar ejecutar ETL de todas formas para crear la estructura SQLite
        try:
            from etl.etl_pipeline import procesar_etl
            procesar_etl()
        except Exception:
            pass
    finally:
        conn.close()

# Inicializar datos al importar o levantar la app
inicializar_datos_si_vacio()

@app.route('/api/completitud', methods=['GET'])
def get_completitud():
    """Mide la completitud general de los campos obligatorios del DWH."""
    conn, is_mysql = get_db_connection()
    cursor = conn.cursor(dictionary=True) if is_mysql else conn.cursor()
    
    try:
        if is_mysql:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN vehiculos_contados IS NOT NULL THEN 1 ELSE 0 END) as vehiculos,
                    SUM(CASE WHEN peatones_contados IS NOT NULL THEN 1 ELSE 0 END) as peatones,
                    SUM(CASE WHEN total_infracciones IS NOT NULL THEN 1 ELSE 0 END) as infracciones,
                    SUM(CASE WHEN id_interseccion IS NOT NULL THEN 1 ELSE 0 END) as intersecciones,
                    SUM(CASE WHEN id_tiempo IS NOT NULL THEN 1 ELSE 0 END) as tiempos
                FROM fact_observaciones
            """)
            res = cursor.fetchone()
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*),
                    SUM(CASE WHEN vehiculos_contados IS NOT NULL THEN 1 ELSE 0 END),
                    SUM(CASE WHEN peatones_contados IS NOT NULL THEN 1 ELSE 0 END),
                    SUM(CASE WHEN total_infracciones IS NOT NULL THEN 1 ELSE 0 END),
                    SUM(CASE WHEN id_interseccion IS NOT NULL THEN 1 ELSE 0 END),
                    SUM(CASE WHEN id_tiempo IS NOT NULL THEN 1 ELSE 0 END)
                FROM fact_observaciones
            """)
            row = cursor.fetchone()
            res = {
                'total': row[0],
                'vehiculos': row[1] or 0,
                'peatones': row[2] or 0,
                'infracciones': row[3] or 0,
                'intersecciones': row[4] or 0,
                'tiempos': row[5] or 0
            }
            
        total = res['total']
        if total == 0:
            return jsonify({
                "total_registros": 0,
                "completitud_general": 0.0,
                "campos": {"vehiculos_contados": 100.0, "peatones_contados": 100.0, "total_infracciones": 100.0}
            })
            
        # Calcular completitud (tenemos 5 campos obligatorios en fact_observaciones evaluados aquí)
        campos_evaluados = ['vehiculos', 'peatones', 'infracciones', 'intersecciones', 'tiempos']
        total_valores_esperados = total * len(campos_evaluados)
        total_valores_no_nulos = sum(res[c] for c in campos_evaluados)
        
        completitud_general = round((total_valores_no_nulos / total_valores_esperados) * 100, 2)
        
        return jsonify({
            "total_registros": total,
            "completitud_general": completitud_general,
            "campos": {
                "vehiculos_contados": round((res['vehiculos'] / total) * 100, 2),
                "peatones_contados": round((res['peatones'] / total) * 100, 2),
                "total_infracciones": round((res['infracciones'] / total) * 100, 2),
                "id_interseccion": round((res['intersecciones'] / total) * 100, 2),
                "id_tiempo": round((res['tiempos'] / total) * 100, 2)
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/kpi_principal', methods=['GET'])
def get_kpi_principal():
    """Calcula el índice de riesgo por intersección y comparaciones con señalética."""
    conn, is_mysql = get_db_connection()
    cursor = conn.cursor(dictionary=True) if is_mysql else conn.cursor()
    
    try:
        # 1. Riesgo por intersección
        query_interseccion = """
            SELECT di.nombre_interseccion, 
                   AVG(fo.indice_riesgo) as promedio_riesgo,
                   SUM(fo.vehiculos_contados) as vehiculos,
                   SUM(fo.total_infracciones) as infracciones
            FROM fact_observaciones fo
            JOIN dim_intersecciones di ON fo.id_interseccion = di.id_interseccion
            GROUP BY di.nombre_interseccion
            ORDER BY promedio_riesgo DESC
        """
        cursor.execute(query_interseccion)
        rows = cursor.fetchall()
        
        riesgo_intersecciones = []
        for r in rows:
            riesgo_intersecciones.append({
                'interseccion': r['nombre_interseccion'] if is_mysql else r[0],
                'promedio_riesgo': float(r['promedio_riesgo'] if is_mysql else r[1]),
                'vehiculos': int(r['vehiculos'] if is_mysql else r[2]),
                'infracciones': int(r['infracciones'] if is_mysql else r[3])
            })
            
        # Top 3 intersecciones más peligrosas
        top_peligrosas = riesgo_intersecciones[:3]
        
        # 3. Promedio general de riesgo
        promedio_general = 0.0
        if riesgo_intersecciones:
            promedio_general = round(sum(i['promedio_riesgo'] for i in riesgo_intersecciones) / len(riesgo_intersecciones), 2)

        return jsonify({
            "promedio_general_riesgo": promedio_general,
            "riesgo_por_interseccion": riesgo_intersecciones,
            "top_3_peligrosas": top_peligrosas
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/distribucion', methods=['GET'])
def get_distribucion():
    """Obtiene la distribución del total de infracciones por tipo."""
    conn, is_mysql = get_db_connection()
    cursor = conn.cursor(dictionary=True) if is_mysql else conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                SUM(infracciones_cinturon) as cinturon,
                SUM(infracciones_celular) as celular,
                SUM(infracciones_senaletica) as senaletica,
                SUM(infracciones_giro) as giro
            FROM fact_observaciones
        """)
        row = cursor.fetchone()
        
        if is_mysql:
            cinturon = int(row['cinturon'] or 0)
            celular = int(row['celular'] or 0)
            senaletica = int(row['senaletica'] or 0)
            giro = int(row['giro'] or 0)
        else:
            cinturon = int(row[0] or 0)
            celular = int(row[1] or 0)
            senaletica = int(row[2] or 0)
            giro = int(row[3] or 0)
            
        total = cinturon + celular + senaletica + giro
        
        return jsonify({
            "total_infracciones": total,
            "distribucion": [
                {"tipo": "Uso de Celular", "cantidad": celular, "porcentaje": round((celular/total)*100, 2) if total > 0 else 0},
                {"tipo": "Sin Cinturón", "cantidad": cinturon, "porcentaje": round((cinturon/total)*100, 2) if total > 0 else 0},
                {"tipo": "No Respetar Señalética", "cantidad": senaletica, "porcentaje": round((senaletica/total)*100, 2) if total > 0 else 0},
                {"tipo": "Giro Indebido", "cantidad": giro, "porcentaje": round((giro/total)*100, 2) if total > 0 else 0}
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/sla', methods=['GET'])
def get_sla():
    """Genera el estado en semáforo de las 5 dimensiones SLA."""
    conn, is_mysql = get_db_connection()
    cursor = conn.cursor(dictionary=True) if is_mysql else conn.cursor()
    
    try:
        # 1. Freshness (Fecha de la última carga)
        cursor.execute("SELECT MAX(fecha) as max_fecha FROM dim_tiempo")
        row = cursor.fetchone()
        max_fecha_str = (row['max_fecha'] if is_mysql else row[0]) or "2026-07-01"
        
        if isinstance(max_fecha_str, str):
            ultima_carga = dt.strptime(max_fecha_str, '%Y-%m-%d').date()
        else:
            ultima_carga = max_fecha_str
            max_fecha_str = max_fecha_str.strftime('%Y-%m-%d')
            
        dias_frescura = (datetime.date.today() - ultima_carga).days
        # Forzar un número coherente en simulación si da negativo (por zonas horarias)
        if dias_frescura < 0:
            dias_frescura = 0
            
        estado_frescura = 'verde' if dias_frescura <= 30 else ('amarillo' if dias_frescura <= 45 else 'rojo')
        
        # 2. Completitud
        completitud_resp = get_completitud().get_json()
        pct_completitud = float(completitud_resp.get('completitud_general', 100.0))
        estado_completitud = 'verde' if pct_completitud >= 95.0 else ('amarillo' if pct_completitud >= 90.0 else 'rojo')
        
        # 3. Latencia del Pipeline & Error Rate (desde log_etl)
        if is_mysql:
            cursor.execute("SELECT duracion_segundos, registros_error, total_procesados FROM log_etl ORDER BY id_log DESC LIMIT 1")
            log = cursor.fetchone()
        else:
            cursor.execute("SELECT duracion_segundos, registros_error, total_procesados FROM log_etl ORDER BY id_log DESC LIMIT 1")
            row_l = cursor.fetchone()
            log = {
                'duracion_segundos': row_l[0] if row_l else 10,
                'registros_error': row_l[1] if row_l else 0,
                'total_procesados': row_l[2] if row_l else 60
            } if row_l else None

        duracion_seg = log['duracion_segundos'] if log else 12  # default mock
        duracion_min = round(duracion_seg / 60, 2)
        estado_latencia = 'verde' if duracion_min <= 3.0 else ('amarillo' if duracion_min <= 6.0 else 'rojo')
        
        errores_etl = log['registros_error'] if log else 0
        total_proc = log['total_procesados'] if log else 60
        tasa_error = round((errores_etl / total_proc) * 100, 2) if total_proc > 0 else 0.0
        estado_error = 'verde' if tasa_error <= 1.0 else ('amarillo' if tasa_error <= 2.0 else 'rojo')
        
        # 4. Uptime (Disponibilidad del Sistema - Simulado en 100% de operación estable)
        uptime_val = 99.9
        estado_uptime = 'verde'

        # SLA Global: Si alguno es rojo, el global es rojo. Si no, si alguno es amarillo, el global es amarillo.
        estados = [estado_frescura, estado_completitud, estado_latencia, estado_error, estado_uptime]
        if 'rojo' in estados:
            estado_global = 'rojo'
        elif 'amarillo' in estados:
            estado_global = 'amarillo'
        else:
            estado_global = 'verde'

        return jsonify({
            "global": estado_global,
            "frescura": {"valor": dias_frescura, "unidad": "días", "estado": estado_frescura, "fecha_ultima_carga": max_fecha_str},
            "completitud": {"valor": pct_completitud, "unidad": "%", "estado": estado_completitud},
            "latencia_etl": {"valor": duracion_seg, "unidad": "segundos", "estado": estado_latencia},
            "tasa_error_etl": {"valor": tasa_error, "unidad": "%", "estado": estado_error},
            "uptime_dashboard": {"valor": uptime_val, "unidad": "%", "estado": estado_uptime},
            "timestamp_evaluacion": dt.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/historico', methods=['GET'])
def get_historico():
    """Retorna los datos de auditoría históricos de observaciones para la tabla del dashboard."""
    conn, is_mysql = get_db_connection()
    cursor = conn.cursor(dictionary=True) if is_mysql else conn.cursor()
    
    try:
        # Consultar las observaciones ordenadas por fecha reciente
        query = """
            SELECT 
                fo.id_observacion, 
                di.nombre_interseccion, 
                dt.fecha, 
                dt.hora_inicio, 
                dt.hora_fin, 
                dt.bloque_horario, 
                fo.vehiculos_contados, 
                fo.peatones_contados, 
                fo.total_infracciones, 
                fo.indice_riesgo
            FROM fact_observaciones fo
            JOIN dim_intersecciones di ON fo.id_interseccion = di.id_interseccion
            JOIN dim_tiempo dt ON fo.id_tiempo = dt.id_tiempo
            ORDER BY dt.fecha DESC, dt.hora_inicio DESC
            LIMIT 100
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        observaciones = []
        total_vehiculos = 0
        total_peatones = 0
        
        for r in rows:
            if is_mysql:
                obs = {
                    'id': r['id_observacion'],
                    'interseccion': r['nombre_interseccion'],
                    'fecha': str(r['fecha']),
                    'horario': f"{r['hora_inicio']} - {r['hora_fin']}",
                    'bloque': r['bloque_horario'],
                    'vehiculos': r['vehiculos_contados'],
                    'peatones': r['peatones_contados'],
                    'infracciones': r['total_infracciones'],
                    'indice_riesgo': float(r['indice_riesgo'])
                }
            else:
                obs = {
                    'id': r[0],
                    'interseccion': r[1],
                    'fecha': r[2],
                    'horario': f"{r[3]} - {r[4]}",
                    'bloque': r[5],
                    'vehiculos': r[6],
                    'peatones': r[7],
                    'infracciones': r[8],
                    'indice_riesgo': float(r[9])
                }
            observaciones.append(obs)
            total_vehiculos += obs['vehiculos']
            total_peatones += obs['peatones']
            
        # Agrupamiento por bloque horario para tendencias
        query_tendencia = """
            SELECT dt.bloque_horario, 
                   SUM(fo.vehiculos_contados) as vehiculos,
                   AVG(fo.indice_riesgo) as promedio_riesgo
            FROM fact_observaciones fo
            JOIN dim_tiempo dt ON fo.id_tiempo = dt.id_tiempo
            GROUP BY dt.bloque_horario
        """
        cursor.execute(query_tendencia)
        rows_t = cursor.fetchall()
        
        tendencia_bloques = []
        for r in rows_t:
            tendencia_bloques.append({
                'bloque': r['bloque_horario'] if is_mysql else r[0],
                'vehiculos': int(r['vehiculos'] if is_mysql else r[1]),
                'promedio_riesgo': float(r['promedio_riesgo'] if is_mysql else r[2])
            })

        return jsonify({
            "total_vehiculos_acumulado": total_vehiculos,
            "total_peatones_acumulado": total_peatones,
            "registros_count": len(observaciones),
            "observaciones": observaciones,
            "tendencia_bloques": tendencia_bloques
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    
    print("\n" + "="*70)
    print(" 🚀 SERVIDOR API REST DE SEGURIDAD VIAL INICIADO CON ÉXITO")
    print("="*70)
    print(" Endpoints de la API listos para su uso:")
    print(f"  👉 http://localhost:{port}/api/historico")
    print(f"  👉 http://localhost:{port}/api/sla")
    print(f"  👉 http://localhost:{port}/api/distribucion")
    print(f"  👉 http://localhost:{port}/api/kpi_principal")
    print(f"  👉 http://localhost:{port}/api/completitud")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=port)
