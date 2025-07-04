-- MySQL dump 10.13  Distrib 9.3.0, for macos14.7 (arm64)
--
-- Host: localhost    Database: inventory_system
-- ------------------------------------------------------
-- Server version	9.3.0

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
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `price` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2111213 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (11,'復刻成功夏季運動上衣','衣物',200),(12,'燈塔T恤（東方藍）','衣物',350),(13,'三代校徽紀念T恤','衣物',350),(14,'燈塔繡章POLO衫（藏青）','衣物',500),(15,'運動短褲','衣物',500),(16,'Champion聯名T恤','衣物',600),(17,'炫彩排汗運動T恤','衣物',750),(18,'經典紀念刺繡T恤','衣物',800),(19,'燈塔刷毛連帽外套','衣物',900),(21,'商務電腦雙肩包','背包',1200),(22,'百搭旅行牛津包','背包',1100),(23,'復刻帆布小書包','背包',600),(24,'百週年校慶紀念帆布袋','背包',350),(31,'啤酒杯','杯具',300),(32,'保溫杯','杯具',1200),(33,'contigo聯名運動水壺','杯具',500),(34,'環保布餐具組','杯具',300),(35,'校歌紀念馬克杯','杯具',300),(36,'校訓金爵玻璃杯','杯具',200),(37,'校徽紀念攪拌匙','杯具',150),(38,'三代校徽珪藻土杯墊','杯具',150),(40,'百週年特刊','特刊',2000),(51,'Parker聯名紀念鋼珠筆','文具',2000),(52,'Parker聯名紀念原子筆','文具',1000),(61,'CG棒球帽','帽子',200),(62,'燈塔棒球帽','帽子',300),(71,'三代校徽磁鐵','徽章磁鐵',50),(72,'成功中學校徽章','徽章磁鐵',100),(73,'成功高中校徽章','徽章磁鐵',100),(74,'建校百週年紀念徽章','徽章磁鐵',100),(81,'校徽抱枕','配件',500),(82,'《成功高中建校一百週年》紀念郵票','配件',300),(83,'伸縮扣證件夾','配件',200),(84,'鋁合金行李吊牌','配件',100),(85,'檜木手機架鑰匙圈','配件',100),(86,'紀念文件夾','配件',20),(87,'無印文具組','配件',600),(88,'青年鑰匙圈','配件',150),(89,'燙金紀念籃球','配件',1200),(91,'成功機能後背包','新品',1200),(92,'成功燙印行李吊牌','新品',350),(93,'上河圖資料夾','新品',50),(94,'成功回憶行李束帶','新品',400),(101,'成功紀念棒球外套(CG)','預購',1300),(102,'成功紀念棒球外套(GK)','預購',1300),(110,'Champion聯名長袖大學T（純淨白）','衣物',1200),(111,'	Champion聯名長袖大學T（藏青）','衣物',1200),(200,'校友會布章','配件',0),(801,'運動毛巾','配件',400),(802,'書包造型悠遊卡','配件',500);
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `product_styles`
--

DROP TABLE IF EXISTS `product_styles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_styles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int DEFAULT NULL,
  `style_name` varchar(50) DEFAULT NULL,
  `center_stock` int DEFAULT NULL,
  `warehouse_stock` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `product_styles_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9002 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_styles`
--

LOCK TABLES `product_styles` WRITE;
/*!40000 ALTER TABLE `product_styles` DISABLE KEYS */;
INSERT INTO `product_styles` VALUES (111,11,'M',4,22),(112,11,'2XL',1,0),(113,11,'3XL',4,19),(121,12,'S',4,4),(122,12,'M',3,13),(123,12,'L',1,0),(124,12,'XL',3,2),(125,12,'2XL',1,0),(131,13,'S',0,15),(132,13,'M',0,1),(133,13,'L',0,0),(134,13,'XL',0,0),(135,13,'2XL',0,0),(141,14,'S',4,0),(142,14,'M',0,0),(143,14,'L',0,0),(144,14,'XL',0,0),(153,15,'L',1,0),(154,15,'XL',2,20),(155,15,'2XL',5,11),(156,15,'3XL',3,10),(157,15,'5XL',3,5),(161,16,'S',5,8),(162,16,'M',5,1),(163,16,'L',0,0),(164,16,'XL',3,6),(165,16,'2XL',3,7),(171,17,'S',6,12),(172,17,'M',1,11),(173,17,'L',2,4),(174,17,'XL',3,3),(175,17,'2XL',10,17),(176,17,'3XL',1,14),(182,18,'M',0,0),(183,18,'L',0,0),(184,18,'XL',0,54),(185,18,'2XL',5,125),(186,18,'3XL',3,3),(191,19,'S',5,4),(192,19,'M',7,45),(193,19,'L',2,10),(194,19,'XL',0,2),(195,19,'2XL',0,0),(210,21,'單一款式',1,4),(221,22,'丹寧藍',3,1),(222,22,'極致黑',1,23),(230,23,'單一款式',9,10),(241,24,'米白',13,300),(242,24,'黑金',19,277),(310,31,'單一款式',10,86),(321,32,'群青藍',3,20),(322,32,'沁涼藍',2,17),(323,32,'極致黑',2,6),(331,33,'橘',14,6),(332,33,'紫',3,13),(333,33,'湖綠',1,1),(334,33,'藍',7,7),(335,33,'螢綠',2,17),(336,33,'灰',0,0),(340,34,'單一款式',9,0),(350,35,'單一款式',2,224),(360,36,'單一款式',6,184),(370,37,'單一款式',4,145),(380,38,'單一款式',5,118),(400,40,'單一款式',0,202),(510,51,'單一款式',4,0),(521,52,'藍',4,0),(522,52,'紅',5,0),(610,61,'單一款式',5,17),(621,62,'中學',9,38),(622,62,'高中',15,119),(711,71,'北二中',46,213),(712,71,'校友會',45,164),(713,71,'高中',71,40),(720,72,'單一款式',170,177),(731,73,'成功藍經典版',81,285),(732,73,'玫瑰金特別版',81,168),(740,74,'單一款式',114,0),(811,81,'純正藍',4,65),(812,81,'天空藍',4,17),(820,82,'單一款式',0,85),(830,83,'單一款式',15,297),(840,84,'單一款式',4,339),(850,85,'單一款式',15,301),(860,86,'單一款式',0,386),(870,87,'單一款式',5,113),(880,88,'單一款式',1,172),(890,89,'單一款式',0,32),(910,91,'單一款式',0,76),(921,92,'新制服',21,278),(922,92,'北二中制服',19,108),(930,93,'單一款式',0,975),(940,94,'單一款式',10,34),(1011,101,'S',100,0),(1012,101,'M',100,0),(1013,101,'L',100,0),(1014,101,'XL',100,0),(1015,101,'2XL',100,0),(1016,101,'3XL',100,0),(1017,101,'4XL',100,0),(1018,101,'5XL',100,0),(1021,102,'S',100,0),(1022,102,'M',100,0),(1023,102,'L',100,0),(1024,102,'XL',100,0),(1025,102,'2XL',100,0),(1026,102,'3XL',100,0),(1027,102,'4XL',100,0),(1028,102,'5XL',100,0),(1100,110,'售完',0,0),(1111,111,'S',4,4),(1112,111,'M',3,13),(1113,111,'L',1,0),(1114,111,'XL',3,2),(1115,111,'2XL',1,0),(2000,200,'非賣品',138,0),(8011,801,'青年各努力',7,218),(8012,801,'Get Ready To Sweat',5,258),(8020,802,'單一款式',4,395);
/*!40000 ALTER TABLE `product_styles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staff`
--

DROP TABLE IF EXISTS `staff`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staff` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `account` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account` (`account`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staff`
--

LOCK TABLES `staff` WRITE;
/*!40000 ALTER TABLE `staff` DISABLE KEYS */;
INSERT INTO `staff` VALUES (1,'陳家平','1922','陳家平'),(2,'蘇昱誠','1118','蘇昱誠'),(3,'楊睿凱','38203676','楊睿凱'),(4,'陳麒宇','1010','1010'),(17,'楊凱翔','0000','yangkaixiang');
/*!40000 ALTER TABLE `staff` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-04 14:57:20
