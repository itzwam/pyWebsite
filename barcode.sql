-- Database structure for compatibilitt with the python code

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

CREATE DATABASE IF NOT EXISTS `barcode` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `barcode`;


CREATE TABLE `info` (
  `id` int(11) NOT NULL,
  `code` varchar(16) NOT NULL,
  `description` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `info` ADD PRIMARY KEY (`id`);

ALTER TABLE `info` MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=0;