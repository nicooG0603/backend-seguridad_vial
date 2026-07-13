# Guía de Implementación del ETL en Pentaho CE 9.4

Este documento detalla los pasos para construir el pipeline ETL utilizando **Pentaho Data Integration (PDI) 9.4 (Kettle)** de forma que replique la lógica exacta de nuestro DWH simplificado y cumpla con la rúbrica del proyecto.

---

## 1. Estructura General del Job / Transformación en Pentaho

Para cargar nuestro modelo estrella de 2 dimensiones (`dim_intersecciones` y `dim_tiempo`), se recomienda diseñar una **Transformación (`.ktr`)** con las siguientes etapas lógicas:

```text
[ CSV file input ] (datos_crudos.csv)
       │
       ▼
[ Select values ] (Casting y renombrado de tipos)
       │
       ├───────────────────────────────┐
       ▼                               ▼
[ Normalización Bloques ]      [ Cálculo de Infracciones ]
(Mapeo de hora a bloque)       (total_infracciones y riesgo)
       │                               │
       └───────────────┬───────────────┘
                        ▼
              [ Database Lookups ]
              (Obtener IDs de dim_intersecciones y dim_tiempo)
                        │
                        ▼
              [ Table Output: fact_observaciones ]
```

---

## 2. Configuración de Pasos (Steps) Detallados

### Paso 1: CSV file input (Lectura de Origen)
*   **Nombre del paso:** `Lectura Observaciones Crudas`
*   **File/Directory:** Seleccionar la ruta del archivo `etl/datos_crudos.csv`.
*   **Delimiter:** `,`
*   **Enclosure:** `"`
*   **Campos:** Definir los tipos de datos correctos (`String` para intersección y estado_senaletica, `Integer` para conteos e infracciones, `Date` con formato `yyyy-MM-dd` para fecha).

### Paso 2: Calculator / Modified Java Script Value (Transformación de Datos)
*   **Cálculo 1 (Total Infracciones):**
    *   Fórmula: `infracciones_cinturon + infracciones_celular + infracciones_senaletica + infracciones_giro`.
*   **Cálculo 2 (Índice de Riesgo):**
    *   Fórmula: `(total_infracciones / vehiculos_contados) * 100`.
*   **Cálculo 3 (Normalización de Horario a Bloques de 24h):**
    *   Utilizar un script JS sencillo para mapear la columna `hora_inicio`:
        ```javascript
        var hora = parseInt(hora_inicio.substring(0,2));
        var bloque_horario = "Tarde-Noche (17:00-19:00)";
        if (hora >= 6 && hora < 12) {
            bloque_horario = "Mañana (07:00-09:00)";
        } else if (hora >= 12 && hora < 17) {
            bloque_horario = "Tarde (12:00-14:00)";
        }
        ```

### Paso 3: Carga de Dimensiones (Combination Lookup/Update)
Dado que las dimensiones `dim_intersecciones` y `dim_tiempo` deben almacenar registros únicos y retornar sus llaves primarias autogeneradas (`id_interseccion` y `id_tiempo`), se deben usar los siguientes pasos:
1.  **Combination lookup/update (`dim_intersecciones`):**
    *   Target table: `dim_intersecciones`.
    *   Buscar clave en tabla: `nombre_interseccion`.
    *   Si no existe, la inserta automáticamente.
    *   Retorna `id_interseccion` al flujo de la transformación.
2.  **Combination lookup/update (`dim_tiempo`):**
    *   Target table: `dim_tiempo`.
    *   Buscar claves en tabla: `fecha`, `hora_inicio`, `hora_fin`.
    *   Si no existe, la inserta agregando el campo calculado `bloque_horario`.
    *   Retorna `id_tiempo` al flujo.

### Paso 4: Table Output (Carga de la Tabla de Hechos)
*   **Nombre del paso:** `Carga fact_observaciones`
*   **Target schema:** vacío o `dwh_seguridad_vial`.
*   **Target table:** `fact_observaciones`.
*   **Specify database fields:** Habilitar.
*   **Mapear campos del flujo a la base de datos:**
    *   `id_interseccion` ➔ `id_interseccion`
    *   `id_tiempo` ➔ `id_tiempo`
    *   `vehiculos_contados` ➔ `vehiculos_contados`
    *   `peatones_contados` ➔ `peatones_contados`
    *   `infracciones_cinturon` ➔ `infracciones_cinturon`
    *   `infracciones_celular` ➔ `infracciones_celular`
    *   `infracciones_senaletica` ➔ `infracciones_senaletica`
    *   `infracciones_giro` ➔ `infracciones_giro`
    *   `total_infracciones` ➔ `total_infracciones`
    *   `indice_riesgo` ➔ `indice_riesgo`
