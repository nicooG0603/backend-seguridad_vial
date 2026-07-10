const db = require('../config/db');

// GET /api/kpis/generales
exports.getKpisGenerales = async (req, res) => {
  try {
    const query = `
      SELECT 
        COALESCE(SUM(vehiculos_15min), 0) AS total_vehiculos, 
        COALESCE(SUM(peatones_15min), 0) AS total_peatones, 
        COALESCE(SUM(total_infracciones), 0) AS total_infracciones 
      FROM fact_observacion_vial
    `;
    const [rows] = await db.query(query);
    const data = rows[0];
    
    return res.status(200).json({
      total_vehiculos: Number(data.total_vehiculos),
      total_peatones: Number(data.total_peatones),
      total_infracciones: Number(data.total_infracciones)
    });
  } catch (error) {
    console.error('Error en getKpisGenerales:', error);
    return res.status(500).json({ 
      error: 'Error interno del servidor al obtener los KPIs generales.',
      details: error.message 
    });
  }
};

// GET /api/intersecciones/riesgo
exports.getRiesgoIntersecciones = async (req, res) => {
  try {
    const query = `
      SELECT 
        di.id_interseccion, 
        di.nombre_interseccion, 
        ROUND(AVG(fov.indice_riesgo), 2) AS promedio_riesgo
      FROM fact_observacion_vial fov
      JOIN dim_interseccion di ON fov.id_interseccion = di.id_interseccion
      GROUP BY di.id_interseccion, di.nombre_interseccion
      ORDER BY promedio_riesgo DESC
    `;
    const [rows] = await db.query(query);
    
    const data = rows.map(row => ({
      id_interseccion: row.id_interseccion,
      nombre_interseccion: row.nombre_interseccion,
      promedio_riesgo: Number(row.promedio_riesgo)
    }));

    return res.status(200).json(data);
  } catch (error) {
    console.error('Error en getRiesgoIntersecciones:', error);
    return res.status(500).json({ 
      error: 'Error interno del servidor al obtener el riesgo de las intersecciones.',
      details: error.message 
    });
  }
};

// GET /api/franjas/analisis
exports.getAnalisisFranjas = async (req, res) => {
  try {
    const query = `
      SELECT 
        franja_horaria, 
        ROUND(AVG(vehiculos_15min), 2) AS promedio_vehiculos, 
        ROUND(AVG(indice_riesgo), 2) AS promedio_riesgo
      FROM fact_observacion_vial
      WHERE franja_horaria IN ('Mañana', 'Mediodía', 'Tarde')
      GROUP BY franja_horaria
    `;
    const [rows] = await db.query(query);
    
    const data = rows.map(row => ({
      franja_horaria: row.franja_horaria,
      promedio_vehiculos: Number(row.promedio_vehiculos),
      promedio_riesgo: Number(row.promedio_riesgo)
    }));

    return res.status(200).json(data);
  } catch (error) {
    console.error('Error en getAnalisisFranjas:', error);
    return res.status(500).json({ 
      error: 'Error interno del servidor al analizar las franjas horarias.',
      details: error.message 
    });
  }
};

// GET /api/infracciones/distribucion
exports.getDistribucionInfracciones = async (req, res) => {
  try {
    const query = `
      SELECT 
        COALESCE(SUM(infraccion_cinturon), 0) AS cinturon, 
        COALESCE(SUM(infraccion_celular), 0) AS celular, 
        COALESCE(SUM(infraccion_senaletica), 0) AS senaletica, 
        COALESCE(SUM(infraccion_giro), 0) AS giro
      FROM fact_observacion_vial
    `;
    const [rows] = await db.query(query);
    const data = rows[0];

    return res.status(200).json({
      cinturon: Number(data.cinturon),
      celular: Number(data.celular),
      senaletica: Number(data.senaletica),
      giro: Number(data.giro)
    });
  } catch (error) {
    console.error('Error en getDistribucionInfracciones:', error);
    return res.status(500).json({ 
      error: 'Error interno del servidor al obtener la distribución de infracciones.',
      details: error.message 
    });
  }
};
