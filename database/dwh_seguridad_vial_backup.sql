-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: dwh_seguridad_vial
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `dim_intersecciones`
--

DROP TABLE IF EXISTS `dim_intersecciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dim_intersecciones` (
  `id_interseccion` int NOT NULL AUTO_INCREMENT,
  `nombre_interseccion` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id_interseccion`),
  UNIQUE KEY `nombre_interseccion` (`nombre_interseccion`)
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dim_intersecciones`
--

LOCK TABLES `dim_intersecciones` WRITE;
/*!40000 ALTER TABLE `dim_intersecciones` DISABLE KEYS */;
INSERT INTO `dim_intersecciones` VALUES (1,'14 la fama / Eduardo Frei Montalva'),(3,'Av Balmaceda / Aníbal Montt'),(6,'Av Dorsal / Anibal Montt'),(5,'Av Dorsal / Av Domingo Santa María'),(4,'Av Dorsal / AV PDTE EDUARDO FREI MONTALVA'),(2,'AV Dorsal / Bravo de Sarabia');
/*!40000 ALTER TABLE `dim_intersecciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dim_tiempo`
--

DROP TABLE IF EXISTS `dim_tiempo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dim_tiempo` (
  `id_tiempo` int NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `hora_inicio` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  `hora_fin` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  `bloque_horario` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id_tiempo`),
  UNIQUE KEY `unique_tiempo` (`fecha`,`hora_inicio`,`hora_fin`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dim_tiempo`
--

LOCK TABLES `dim_tiempo` WRITE;
/*!40000 ALTER TABLE `dim_tiempo` DISABLE KEYS */;
INSERT INTO `dim_tiempo` VALUES (1,'2026-06-15','07:00','07:15','Mañana (07:00-09:00)'),(2,'2026-06-15','07:30','07:45','Mañana (07:00-09:00)'),(3,'2026-06-15','07:45','08:00','Mañana (07:00-09:00)'),(4,'2026-06-15','08:00','08:15','Mañana (07:00-09:00)'),(5,'2026-06-15','08:15','08:30','Mañana (07:00-09:00)'),(6,'2026-06-15','12:30','12:45','Tarde (12:00-14:00)'),(7,'2026-06-15','13:00','13:15','Tarde (12:00-14:00)'),(8,'2026-06-15','13:30','13:45','Tarde (12:00-14:00)'),(9,'2026-06-15','16:00','16:15','Tarde (12:00-14:00)'),(10,'2026-06-15','16:30','16:45','Tarde (12:00-14:00)'),(11,'2026-06-15','17:30','17:45','Tarde-Noche (17:00-19:00)'),(13,'2026-06-15','17:45','18:00','Tarde-Noche (17:00-19:00)'),(14,'2026-06-15','18:30','18:45','Tarde-Noche (17:00-19:00)'),(15,'2026-06-15','19:00','19:15','Tarde-Noche (17:00-19:00)'),(16,'2026-06-16','07:15','07:30','Mañana (07:00-09:00)'),(21,'2026-06-16','12:00','12:15','Tarde (12:00-14:00)'),(22,'2026-06-16','12:30','12:45','Tarde (12:00-14:00)'),(23,'2026-06-16','12:45','13:00','Tarde (12:00-14:00)'),(24,'2026-06-16','13:15','13:30','Tarde (12:00-14:00)'),(25,'2026-06-16','13:45','14:00','Tarde (12:00-14:00)'),(26,'2026-06-16','17:00','17:15','Tarde-Noche (17:00-19:00)'),(27,'2026-06-16','17:15','17:30','Tarde-Noche (17:00-19:00)'),(28,'2026-06-16','17:30','17:45','Tarde-Noche (17:00-19:00)'),(29,'2026-06-16','17:45','18:00','Tarde-Noche (17:00-19:00)'),(30,'2026-06-16','18:30','18:45','Tarde-Noche (17:00-19:00)'),(31,'2026-06-22','08:00','08:15','Mañana (07:00-09:00)'),(32,'2026-06-22','08:15','08:30','Mañana (07:00-09:00)'),(33,'2026-06-22','08:30','08:45','Mañana (07:00-09:00)'),(35,'2026-06-22','08:45','09:00','Mañana (07:00-09:00)'),(36,'2026-06-22','13:30','13:45','Tarde (12:00-14:00)'),(37,'2026-06-22','13:45','14:00','Tarde (12:00-14:00)'),(40,'2026-06-22','17:15','17:30','Tarde-Noche (17:00-19:00)'),(42,'2026-06-22','17:45','18:00','Tarde-Noche (17:00-19:00)'),(44,'2026-06-22','18:00','18:15','Tarde-Noche (17:00-19:00)'),(45,'2026-06-22','18:15','18:30','Tarde-Noche (17:00-19:00)'),(46,'2026-06-23','07:15','07:30','Mañana (07:00-09:00)'),(47,'2026-06-23','07:30','07:45','Mañana (07:00-09:00)'),(48,'2026-06-23','07:45','08:00','Mañana (07:00-09:00)'),(49,'2026-06-23','08:00','08:15','Mañana (07:00-09:00)'),(50,'2026-06-23','08:30','08:45','Mañana (07:00-09:00)'),(51,'2026-06-23','12:15','12:30','Tarde (12:00-14:00)'),(53,'2026-06-23','13:00','13:15','Tarde (12:00-14:00)'),(54,'2026-06-23','13:15','13:30','Tarde (12:00-14:00)'),(55,'2026-06-23','13:30','13:45','Tarde (12:00-14:00)'),(56,'2026-06-23','17:15','17:30','Tarde-Noche (17:00-19:00)'),(57,'2026-06-23','17:45','18:00','Tarde-Noche (17:00-19:00)'),(58,'2026-06-23','18:45','19:00','Tarde-Noche (17:00-19:00)');
/*!40000 ALTER TABLE `dim_tiempo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fact_observaciones`
--

DROP TABLE IF EXISTS `fact_observaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fact_observaciones` (
  `id_observacion` int NOT NULL AUTO_INCREMENT,
  `id_interseccion` int NOT NULL,
  `id_tiempo` int NOT NULL,
  `vehiculos_contados` int NOT NULL,
  `peatones_contados` int NOT NULL,
  `infracciones_cinturon` int NOT NULL,
  `infracciones_celular` int NOT NULL,
  `infracciones_senaletica` int NOT NULL,
  `infracciones_giro` int NOT NULL,
  `total_infracciones` int NOT NULL,
  `indice_riesgo` decimal(5,2) NOT NULL,
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_observacion`),
  KEY `id_interseccion` (`id_interseccion`),
  KEY `id_tiempo` (`id_tiempo`),
  CONSTRAINT `fact_observaciones_ibfk_1` FOREIGN KEY (`id_interseccion`) REFERENCES `dim_intersecciones` (`id_interseccion`) ON DELETE CASCADE,
  CONSTRAINT `fact_observaciones_ibfk_2` FOREIGN KEY (`id_tiempo`) REFERENCES `dim_tiempo` (`id_tiempo`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fact_observaciones`
--

LOCK TABLES `fact_observaciones` WRITE;
/*!40000 ALTER TABLE `fact_observaciones` DISABLE KEYS */;
INSERT INTO `fact_observaciones` VALUES (1,1,1,359,68,24,33,34,27,118,32.87,'2026-07-12 23:42:23'),(2,2,2,346,22,25,11,25,29,90,26.01,'2026-07-12 23:42:23'),(3,3,3,253,46,12,3,8,9,32,12.65,'2026-07-12 23:42:23'),(4,4,4,329,24,16,12,14,20,62,18.84,'2026-07-12 23:42:23'),(5,5,5,382,36,29,9,16,14,68,17.80,'2026-07-12 23:42:23'),(6,5,6,445,38,36,26,32,37,131,29.44,'2026-07-12 23:42:23'),(7,3,7,225,24,17,6,13,10,46,20.44,'2026-07-12 23:42:23'),(8,1,8,290,21,22,27,25,37,111,38.28,'2026-07-12 23:42:23'),(9,2,9,234,9,36,3,13,37,89,38.03,'2026-07-12 23:42:23'),(10,4,10,489,44,64,31,17,18,130,26.58,'2026-07-12 23:42:23'),(11,3,11,303,44,24,9,13,12,58,19.14,'2026-07-12 23:42:23'),(12,5,11,496,87,32,21,44,40,137,27.62,'2026-07-12 23:42:23'),(13,1,13,500,60,67,47,45,66,225,45.00,'2026-07-12 23:42:23'),(14,2,14,456,43,51,9,32,57,149,32.68,'2026-07-12 23:42:23'),(15,4,15,492,93,36,25,22,15,98,19.92,'2026-07-12 23:42:23'),(16,1,16,386,83,51,14,36,55,156,40.41,'2026-07-12 23:42:23'),(17,3,16,244,45,10,5,10,7,32,13.11,'2026-07-12 23:42:23'),(18,5,16,376,65,20,9,11,21,61,16.22,'2026-07-12 23:42:23'),(19,4,16,349,71,31,9,16,19,75,21.49,'2026-07-12 23:42:23'),(20,2,16,284,19,17,16,22,18,73,25.70,'2026-07-12 23:42:23'),(21,3,21,182,37,11,9,8,4,32,17.58,'2026-07-12 23:42:23'),(22,2,22,301,40,21,16,26,25,88,29.24,'2026-07-12 23:42:23'),(23,4,23,305,64,28,16,14,14,72,23.61,'2026-07-12 23:42:23'),(24,1,24,346,44,32,24,34,21,111,32.08,'2026-07-12 23:42:23'),(25,5,25,397,58,45,28,25,19,117,29.47,'2026-07-12 23:42:23'),(26,5,26,500,37,44,22,29,44,139,27.80,'2026-07-12 23:42:23'),(27,3,27,304,29,18,10,17,21,66,21.71,'2026-07-12 23:42:23'),(28,1,28,452,58,58,16,26,34,134,29.65,'2026-07-12 23:42:23'),(29,4,29,546,105,29,8,31,40,108,19.78,'2026-07-12 23:42:23'),(30,2,30,414,42,44,11,23,27,105,25.36,'2026-07-12 23:42:23'),(31,2,31,385,39,46,18,21,41,126,32.73,'2026-07-12 23:42:23'),(32,3,32,257,37,22,9,6,7,44,17.12,'2026-07-12 23:42:23'),(33,5,33,513,91,32,18,21,29,100,19.49,'2026-07-12 23:42:23'),(34,1,33,330,23,32,16,25,32,105,31.82,'2026-07-12 23:42:23'),(35,4,35,451,68,32,7,11,26,76,16.85,'2026-07-12 23:42:23'),(36,2,36,271,58,27,14,20,9,70,25.83,'2026-07-12 23:42:23'),(37,5,37,365,74,19,21,29,12,81,22.19,'2026-07-12 23:42:23'),(38,3,37,229,49,8,6,11,13,38,16.59,'2026-07-12 23:42:23'),(39,4,37,311,54,15,9,15,11,50,16.08,'2026-07-12 23:42:23'),(40,1,40,453,27,75,23,42,64,204,45.03,'2026-07-12 23:42:23'),(41,2,40,458,39,62,11,18,35,126,27.51,'2026-07-12 23:42:23'),(42,3,42,316,39,23,6,18,21,68,21.52,'2026-07-12 23:42:23'),(43,5,42,585,59,68,31,32,18,149,25.47,'2026-07-12 23:42:23'),(44,4,44,556,34,41,20,14,28,103,18.53,'2026-07-12 23:42:23'),(45,1,45,586,105,11,9,25,35,80,13.65,'2026-07-12 23:42:23'),(46,2,46,277,49,22,21,21,27,91,32.85,'2026-07-12 23:42:23'),(47,5,47,469,52,42,28,28,43,141,30.06,'2026-07-12 23:42:23'),(48,3,48,232,40,13,7,6,13,39,16.81,'2026-07-12 23:42:23'),(49,4,49,372,52,28,18,12,8,66,17.74,'2026-07-12 23:42:23'),(50,1,50,297,49,31,15,32,35,113,38.05,'2026-07-12 23:42:23'),(51,4,51,400,40,16,12,20,15,63,15.75,'2026-07-12 23:42:23'),(52,3,51,180,33,14,6,7,13,40,22.22,'2026-07-12 23:42:23'),(53,5,53,370,61,39,9,32,18,98,26.49,'2026-07-12 23:42:23'),(54,2,54,320,24,41,22,13,30,106,33.12,'2026-07-12 23:42:23'),(55,1,55,325,36,49,23,18,36,126,38.77,'2026-07-12 23:42:23'),(56,4,56,496,49,39,6,29,25,99,19.96,'2026-07-12 23:42:23'),(57,2,57,453,90,31,26,24,23,104,22.96,'2026-07-12 23:42:23'),(58,1,58,489,77,50,34,19,34,137,28.02,'2026-07-12 23:42:23'),(59,3,58,308,51,29,12,18,21,80,25.97,'2026-07-12 23:42:23'),(60,5,58,502,32,36,24,40,17,117,23.31,'2026-07-12 23:42:23');
/*!40000 ALTER TABLE `fact_observaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log_etl`
--

DROP TABLE IF EXISTS `log_etl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `log_etl` (
  `id_log` int NOT NULL AUTO_INCREMENT,
  `timestamp_inicio` datetime NOT NULL,
  `timestamp_fin` datetime DEFAULT NULL,
  `duracion_segundos` int DEFAULT NULL,
  `total_procesados` int DEFAULT '0',
  `registros_cargados` int DEFAULT '0',
  `registros_error` int DEFAULT '0',
  `estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'exitoso',
  `mensaje_error` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id_log`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log_etl`
--

LOCK TABLES `log_etl` WRITE;
/*!40000 ALTER TABLE `log_etl` DISABLE KEYS */;
INSERT INTO `log_etl` VALUES (1,'2026-07-12 23:42:23','2026-07-12 23:42:23',0,60,60,0,'exitoso',NULL);
/*!40000 ALTER TABLE `log_etl` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-13  0:15:25
