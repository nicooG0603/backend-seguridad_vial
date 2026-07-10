const express = require('express');
const cors = require('cors');
require('dotenv').config();

const db = require('./src/config/db');
const apiRoutes = require('./src/routes/api');

const app = express();
const PORT = process.env.PORT || 3000;

// Middlewares esenciales
app.use(cors());
app.use(express.json());

// Rutas del API
app.use('/api', apiRoutes);

// Endpoint de verificación rápida (Healthcheck)
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'OK', message: 'Servidor de Seguridad Vial levantado y funcionando.' });
});

// Probar conexión de base de datos e iniciar servidor
async function startServer() {
  try {
    // Intentar obtener una conexión del pool para verificar credenciales
    const connection = await db.getConnection();
    console.log('==================================================');
    console.log(' Conexión exitosa a la base de datos MySQL.');
    console.log('==================================================');
    connection.release();

    app.listen(PORT, () => {
      console.log(` Servidor de Seguridad Vial corriendo en: http://localhost:${PORT}`);
    });
  } catch (error) {
    console.error('==================================================');
    console.error(' ERROR CRÍTICO: No se pudo establecer conexión con MySQL.');
    console.error(` Mensaje de error: ${error.message}`);
    console.error(' Por favor, verifica tu configuración en el archivo `.env`.');
    console.error('==================================================');

    // Iniciamos el servidor de todos modos para que pueda responder peticiones (devolviendo errores HTTP 500)
    app.listen(PORT, () => {
      console.log(` Servidor de Seguridad Vial levantado (SIN conexión a la base de datos) en: http://localhost:${PORT}`);
    });
  }
}

startServer();
