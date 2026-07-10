const express = require('express');
const router = express.Router();
const vialesController = require('../controllers/vialesController');

// Definición de las rutas del API
router.get('/kpis/generales', vialesController.getKpisGenerales);
router.get('/intersecciones/riesgo', vialesController.getRiesgoIntersecciones);
router.get('/franjas/analisis', vialesController.getAnalisisFranjas);
router.get('/infracciones/distribucion', vialesController.getDistribucionInfracciones);

module.exports = router;
