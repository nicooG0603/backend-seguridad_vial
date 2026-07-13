# Guía de Implementación del ETL en Pentaho CE 9.4

Este documento detalla los pasos para construir el pipeline ETL utilizando **Pentaho Data Integration (PDI) 9.4 (Kettle)** de forma que replique la lógica implementada en nuestro pipeline de desarrollo y cumpla con la rúbrica del proyecto.

---

## 1. Estructura General del Job / Transformación en Pentaho

Para cargar el modelo estrella (Star Schema) correctamente, se recomienda diseñar una **Transformación (`.ktr`)** con las siguientes etapas lógicas:

```text
[ CSV file input ]
       │
       ▼
[ Select values ] (Casting y renombrado de tipos)
       │
       ├───────────────────────────────┐
       ▼                               ▼
[ Normalización Bloques ]      [ Cálculo de Métricas ]
(Mapeo de hora a bloque)       (total_infracciones y riesgo)
       │                               │
       └───────────────┬───────────────┘
                       ▼
             [ Database Lookups ]
             (Obtener IDs de Dimensiones)
                       │
                       ▼
             [ Table Output: facts ]
```

---

## 2. Configuración de Pasos (Steps) Detallados

### Paso 1: CSV file input (Lectura de Origen)
*   **Nombre del paso:** `Lectura Observaciones Crudas`
*   **File/Directory:** Seleccionar la ruta del archivo `etl/datos_crudos.csv`.
*   **Delimiter:** `,`
*   **Enclosure:** `"`
*   **Campos:** Definir los tipos de datos correctos (`String` para intersección y señalética, `Integer` para conteos e infracciones, `Date` con formato `yyyy-MM-dd` para fecha).

### Paso 2: Calculator / Modified Java Script Value (Transformación de Datos)
*   **Cálculo 1 (Total Infracciones):**
    *   Fórmula: `infracciones_cinturon + infracciones_celular + infracciones_velocidad`.
*   **Cálculo 2 (Índice de Riesgo):**
    *   Fórmula: `(total_infracciones / vehiculos_contados) * 100`.
*   **Cálculo 3 (Normalización de Horario a Bloques):**
    *   Utilizar un script JS sencillo o una regla de paso "Value Mapper" para mapear la columna `hora_inicio`:
        ```javascript
        var hora = parseInt(hora_inicio.substring(0,2));
        var bloque_horario = "Fuera de Rango";
        if (hora >= 7 && hora < 9) {
            bloque_horario = "Mañana (07:00-09:00)";
        } else if (hora >= 12 && hora < 14) {
            bloque_horario = "Tarde (12:00-14:00)";
        } else if (hora >= 17 && hora < 19) {
            bloque_horario = "Tarde-Noche (17:00-19:00)";
        }
        ```

### Paso 3: Carga de Dimensiones e Inserción Combinada (Combination Lookup/Update)
Dado que las dimensiones `dim_intersecciones` y `dim_tiempo` deben almacenar registros únicos y retornar sus llaves primarias autogeneradas (`id_interseccion` y `id_tiempo`), se deben usar los siguientes pasos:
1.  **Combination lookup/update (`dim_intersecciones`):**
    *   Buscar clave en tabla: `nombre_interseccion`.
    *   Si no existe, la inserta y actualiza la fila agregando la columna `zona`.
    *   Retorna `id_interseccion` al flujo de la transformación.
2.  **Combination lookup/update (`dim_tiempo`):**
    *   Buscar claves en tabla: `fecha`, `hora_inicio`, `hora_fin`.
    *   Inserta y actualiza `bloque_horario`.
    *   Retorna `id_tiempo` al flujo.
3.  **Database lookup (`dim_senaletica`):**
    *   Buscar clave `estado_senaletica` y retornar `id_senaletica`.

### Paso 4: Table Output (Carga de la Tabla de Hechos)
*   **Nombre del paso:** `Carga fact_observaciones`
*   **Target schema:** vacío o `dwh_seguridad_vial`.
*   **Target table:** `fact_observaciones`.
*   **Specify database fields:** Habilitar.
*   **Mapear campos del flujo a la base de datos:**
    *   `id_interseccion` ➔ `id_interseccion`
    *   `id_tiempo` ➔ `id_tiempo`
    *   `id_senaletica` ➔ `id_senaletica`
    *   `vehiculos_contados` ➔ `vehiculos_contados`
    *   `peatones_contados` ➔ `peatones_contados`
    *   `infracciones_cinturon` ➔ `infracciones_cinturon`
    *   `infracciones_celular` ➔ `infracciones_celular`
    *   `infracciones_velocidad` ➔ `infracciones_velocidad`
    *   `total_infracciones` ➔ `total_infracciones`
    *   `indice_riesgo` ➔ `indice_riesgo`
