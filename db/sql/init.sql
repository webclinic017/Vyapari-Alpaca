CREATE DATABASE  IF NOT EXISTS `vyapari` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `vyapari`;
-- MySQL dump 10.13  Distrib 8.0.17, for macos10.14 (x86_64)
--
-- Host: 127.0.0.1    Database: vyapari
-- ------------------------------------------------------
-- Server version	8.0.27

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `account`
--

DROP TABLE IF EXISTS `account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account` (
  `date` date NOT NULL,
  `portfolio_value` decimal(12,2) DEFAULT NULL,
  `buying_power` decimal(12,2) NOT NULL,
  `equity` decimal(12,2) DEFAULT NULL,
  `status` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `initial_margin` decimal(12,2) DEFAULT NULL,
  `pattern_day_trader` tinyint NOT NULL,
  `shorting_enabled` tinyint NOT NULL,
  `created_at` timestamp NOT NULL,
  `updated_at` timestamp NOT NULL,
  PRIMARY KEY (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account`
--

LOCK TABLES `account` WRITE;
/*!40000 ALTER TABLE `account` DISABLE KEYS */;
/*!40000 ALTER TABLE `account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order`
--

DROP TABLE IF EXISTS `order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order` (
  `id` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `parent_id` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `symbol` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `side` varchar(4) COLLATE utf8mb4_unicode_ci NOT NULL,
  `order_qty` int NOT NULL,
  `time_in_force` varchar(6) COLLATE utf8mb4_unicode_ci NOT NULL,
  `order_class` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `order_type` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `trail_percent` decimal(10,2) DEFAULT NULL,
  `trail_price` decimal(10,2) DEFAULT NULL,
  `initial_stop_price` decimal(10,2) DEFAULT NULL,
  `updated_stop_price` decimal(10,2) DEFAULT NULL,
  `failed_at` timestamp NULL DEFAULT NULL,
  `filled_at` timestamp NULL DEFAULT NULL,
  `filled_avg_price` decimal(10,2) DEFAULT NULL,
  `filled_qty` int DEFAULT NULL,
  `hwm` decimal(10,2) DEFAULT NULL,
  `limit_price` decimal(10,2) DEFAULT NULL,
  `replaced_by` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `extended_hours` tinyint DEFAULT NULL,
  `status` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `canceled_at` timestamp NULL DEFAULT NULL,
  `expired_at` timestamp NULL DEFAULT NULL,
  `replaced_at` timestamp NULL DEFAULT NULL,
  `submitted_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL,
  `updated_at` timestamp NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order`
--

LOCK TABLES `order` WRITE;
/*!40000 ALTER TABLE `order` DISABLE KEYS */;
/*!40000 ALTER TABLE `order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `position`
--

DROP TABLE IF EXISTS `position`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `position` (
  `run_date` date NOT NULL,
  `symbol` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `side` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `qty` int NOT NULL,
  `entry_price` decimal(10,2) NOT NULL,
  `market_price` decimal(10,2) NOT NULL,
  `lastday_price` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NOT NULL,
  `updated_at` timestamp NOT NULL,
  PRIMARY KEY (`run_date`,`symbol`,`side`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `position`
--

LOCK TABLES `position` WRITE;
/*!40000 ALTER TABLE `position` DISABLE KEYS */;
INSERT INTO `position` VALUES ('2021-12-22','AAPL','long',10,170.13,175.98,172.99,'2021-12-22 10:51:56','2021-12-22 20:45:25'),('2021-12-22','CNK','long',248,20.19,17.35,17.23,'2021-12-22 10:51:55','2021-12-22 20:45:25'),('2021-12-22','ERF','long',529,9.47,9.91,9.74,'2021-12-22 10:51:55','2021-12-22 20:45:25'),('2021-12-22','EZPW','long',677,7.40,7.09,7.19,'2021-12-22 10:51:55','2021-12-22 20:45:25'),('2021-12-22','GEL','long',440,11.37,10.34,10.02,'2021-12-22 10:51:55','2021-12-22 20:45:25'),('2021-12-22','IGT','long',168,29.80,27.91,27.85,'2021-12-22 10:51:55','2021-12-22 20:45:25'),('2021-12-22','MSFT','long',1,327.08,333.75,327.29,'2021-12-22 10:51:55','2021-12-22 20:45:25'),('2021-12-22','OXY','long',142,35.16,28.93,28.60,'2021-12-22 10:51:55','2021-12-22 20:45:25'),('2021-12-22','RFP','long',374,13.41,13.28,12.85,'2021-12-22 10:51:55','2021-12-22 20:45:25'),('2021-12-22','TDW','long',391,12.79,10.71,10.74,'2021-12-22 10:51:55','2021-12-22 20:45:25'),('2021-12-22','TWLO','long',10,266.95,268.77,276.92,'2021-12-22 10:51:55','2021-12-22 20:45:25'),('2021-12-22','VET','long',437,11.44,12.51,11.71,'2021-12-22 10:51:55','2021-12-22 20:45:25');
/*!40000 ALTER TABLE `position` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-12-22 21:41:17