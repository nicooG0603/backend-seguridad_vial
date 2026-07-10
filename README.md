# Backend - Sistema de Seguridad Vial Urbana

Este es el backend para el proyecto universitario de **Seguridad Vial Urbana**. Es una API REST desarrollada con **Node.js** y **Express** que se conecta a una base de datos **MySQL** para procesar y exponer indicadores clave de rendimiento (KPIs), análisis de riesgo en intersecciones, evolución de riesgo por franja horaria y la distribución de infracciones de tránsito en la ciudad.

---

## 🛠️ Tecnologías Utilizadas

* **Node.js** (Entorno de ejecución para JavaScript)
* **Express** (Framework web para la creación de la API REST)
* **MySQL** (Base de datos relacional para el almacenamiento de hechos y dimensiones)
* **mysql2/promise** (Cliente MySQL con soporte para promesas y Async/Await)
* **CORS** (Middleware para permitir peticiones de origen cruzado desde el Dashboard Frontend)
* **dotenv** (Gestión de variables de entorno seguras)
* **Nodemon** (Herramienta de desarrollo para reinicio automático del servidor)

---

## 📁 Estructura del Proyecto

El proyecto está organizado utilizando una arquitectura limpia de controladores y rutas:

```text
backend-seguridadvial/
│
├── .env                  # Variables de entorno (no se sube al repositorio)
├── .env.example          # Plantilla para configurar las variables de entorno
├── .gitignore            # Exclusión de archivos en Git (node_modules, .env)
├── database_setup.sql    # Script SQL para la creación de tablas y datos semilla
├── package.json          # Dependencias y scripts de ejecución
├── server.js             # Entrada principal del servidor y verificación de DB
│
└── src/
    ├── config/
    │   └── db.js         # Pool de conexiones a MySQL usando mysql2/promise
    ├── controllers/
    │   └── vialesController.js # Lógica de negocio y consultas SQL para los endpoints
    └── routes/
        └── api.js        # Definición y mapeo de las rutas de la API REST
```

---

## 🗄️ Estructura de la Base de Datos

El sistema utiliza un diseño de esquema en estrella compuesto por las siguientes tablas:

### 1. Dimensión Intersección (`dim_interseccion`)
Almacena la información de las esquinas o intersecciones viales controladas.
* `id_interseccion` (INT, PK, Auto_Increment)
* `nombre_interseccion` (VARCHAR, Único, Not Null)
* `calle_principal` (VARCHAR, Not Null)
* `calle_secundaria` (VARCHAR, Not Null)

### 2. Hechos de Observación Vial (`fact_observacion_vial`)
Registra las métricas medidas en bloques de 15 minutos en cada intersección.
* `id_observacion` (INT, PK, Auto_Increment)
* `id_interseccion` (INT, FK referenciando a `dim_interseccion`)
* `fecha_observacion` (DATE, Not Null)
* `franja_horaria` (VARCHAR, Not Null - Valores: 'Mañana', 'Mediodía', 'Tarde')
* `vehiculos_15min` (INT, Not Null)
* `peatones_15min` (INT, Not Null)
* `infraccion_cinturon` (INT, Not Null)
* `infraccion_celular` (INT, Not Null)
* `infraccion_senaletica` (INT, Not Null)
* `infraccion_giro` (INT, Not Null)
* `total_infracciones` (INT, Not Null)
* `indice_riesgo` (DECIMAL, Not Null)

---

## 🚀 Instrucciones de Configuración e Instalación

### Requisitos Previos
Asegúrate de tener instalados:
* [Node.js](https://nodejs.org/) (Versión 16 o superior recomendada)
* Servidor [MySQL](https://www.mysql.com/) (Local o remoto en funcionamiento)

### Paso 1: Configurar la Base de Datos
1. Abre tu gestor de base de datos de preferencia (MySQL Workbench, phpMyAdmin, etc.).
2. Ejecuta el script completo contenido en el archivo **[`database_setup.sql`](./database_setup.sql)**.
   * *Este script creará la base de datos `seguridad_vial`, las tablas correspondientes e insertará datos semilla realistas para que puedas probar la API inmediatamente sin registros vacíos.*

### Paso 2: Clonar y Preparar el Entorno
1. Clona este repositorio:
   ```bash
   git clone https://github.com/nicooG0603/backend-seguridad_vial.git
   cd backend-seguridad_vial
   ```
2. Instala las dependencias del proyecto:
   ```bash
   npm install
   ```

### Paso 3: Configurar Variables de Entorno
1. Crea un archivo llamado **`.env`** en la raíz del proyecto (puedes duplicar y renombrar el archivo `.env.example`).
2. Configura las credenciales correctas para tu base de datos local:
   ```env
   PORT=3000
   DB_HOST=localhost
   DB_USER=tu_usuario_mysql
   DB_PASSWORD=tu_contraseña_mysql
   DB_NAME=seguridad_vial
   DB_PORT=3306
   ```

### Paso 4: Levantar el Servidor
Inicia el servidor en modo desarrollo utilizando Nodemon (se reiniciará automáticamente al guardar cambios):
```bash
npm run dev
```

Si todo está configurado correctamente, verás la siguiente respuesta en consola:
```text
==================================================
 Conexión exitosa a la base de datos MySQL.
==================================================
 Servidor de Seguridad Vial corriendo en: http://localhost:3000
```

---

## 📡 Endpoints de la API REST

Todos los endpoints devuelven respuestas en formato **JSON** y están prefijados con `/api`.

### 1. KPIs Generales
* **Ruta:** `GET /api/kpis/generales`
* **Descripción:** Devuelve el volumen total acumulado de vehículos observados, peatones y la suma global de infracciones registradas en la base de datos.
* **Ejemplo de respuesta:**
  ```json
  {
    "total_vehiculos": 5290,
    "total_peatones": 2770,
    "total_infracciones": 357
  }
  ```

### 2. Top de Intersecciones Peligrosas
* **Ruta:** `GET /api/intersecciones/riesgo`
* **Descripción:** Calcula el índice de riesgo promedio por intersección, ordenado de mayor a menor. Ideal para graficar el "Top de Intersecciones más peligrosas" en el Frontend.
* **Ejemplo de respuesta:**
  ```json
  [
    {
      "id_interseccion": 2,
      "nombre_interseccion": "Av. 9 de Julio y Av. Corrientes",
      "promedio_riesgo": 8.53
    },
    {
      "id_interseccion": 4,
      "nombre_interseccion": "Av. Rivadavia y Av. Acoyte",
      "promedio_riesgo": 5.43
    }
  ]
  ```

### 3. Análisis por Franja Horaria
* **Ruta:** `GET /api/franjas/analisis`
* **Descripción:** Retorna el promedio de flujo vehicular (`vehiculos_15min`) y el índice de riesgo promedio para cada uno de los bloques horarios obligatorios ('Mañana', 'Mediodía', 'Tarde').
* **Ejemplo de respuesta:**
  ```json
  [
    {
      "franja_horaria": "Mañana",
      "promedio_vehiculos": 405,
      "promedio_riesgo": 5.13
    },
    {
      "franja_horaria": "Mediodía",
      "promedio_vehiculos": 422.5,
      "promedio_riesgo": 5.43
    }
  ]
  ```

### 4. Distribución de Infracciones
* **Ruta:** `GET /api/infracciones/distribucion`
* **Descripción:** Sumariza la cantidad total acumulada para cada tipo específico de infracción (cinturón, celular, señalética, giro). Útil para gráficos de torta o barras.
* **Ejemplo de respuesta:**
  ```json
  {
    "cinturon": 86,
    "celular": 141,
    "senaletica": 63,
    "giro": 42
  }
  ```

### 5. Estado de Salud (Healthcheck)
* **Ruta:** `GET /health`
* **Descripción:** Endpoint rápido para validar que el servidor está respondiendo peticiones sin necesidad de consultar la base de datos.
* **Ejemplo de respuesta:**
  ```json
  {
    "status": "OK",
    "message": "Servidor de Seguridad Vial levantado y funcionando."
  }
  ```
