-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 29, 2025 at 10:10 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `battery_swap`
--

-- --------------------------------------------------------

--
-- Table structure for table `appointments`
--

CREATE TABLE `appointments` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `station_id` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `time` time DEFAULT NULL,
  `status` enum('pending','approved','cancelled') DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `appointments`
--

INSERT INTO `appointments` (`id`, `user_id`, `station_id`, `date`, `time`, `status`) VALUES
(8, 3, 2, '2025-06-27', '16:30:00', 'approved'),
(10, 3, 7, '2025-06-27', '15:29:00', 'cancelled'),
(11, 3, 7, '2025-06-28', '15:30:00', 'approved'),
(12, 4, 7, '2025-06-27', '18:00:00', 'approved'),
(13, 4, 7, '2025-06-27', '18:02:00', 'approved'),
(14, 4, 3, '2025-06-27', '19:07:00', 'approved'),
(15, 3, 3, '2025-07-02', '09:00:00', 'approved');

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

CREATE TABLE `feedback` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `q1` int(11) DEFAULT NULL,
  `q2` int(11) DEFAULT NULL,
  `q3` int(11) DEFAULT NULL,
  `q4` int(11) DEFAULT NULL,
  `q5` int(11) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `date_submitted` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `feedback`
--

INSERT INTO `feedback` (`id`, `user_id`, `q1`, `q2`, `q3`, `q4`, `q5`, `message`, `date_submitted`) VALUES
(1, 3, 1, 2, 3, 4, 5, '', '2025-06-29 22:53:53'),
(3, 4, 5, 1, 2, 4, 1, 'no', '2025-06-29 23:03:05');

-- --------------------------------------------------------

--
-- Table structure for table `stations`
--

CREATE TABLE `stations` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `zip_code` varchar(10) DEFAULT NULL,
  `total_batteries` int(11) DEFAULT 0,
  `available_batteries` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `stations`
--

INSERT INTO `stations` (`id`, `name`, `address`, `city`, `zip_code`, `total_batteries`, `available_batteries`) VALUES
(1, 'Swap Station A', '123 MG Road', 'Pune', '411001', 10, 3),
(2, 'Swap Station B', '45 Bandra Lane', 'Mumbai', '400050', 8, 3),
(3, 'Swap Station C', '10 Shahupuri', 'Kolhapur', '416001', 6, 4),
(4, 'EV Fast Swap Hub', '88 Ambazari Road', 'Nagpur', '440010', 0, 0),
(5, 'Battery Zone X', '12 College Road', 'Nashik', '422005', 12, 8),
(6, 'GreenVolt Station', '55 Jalna Road', 'Aurangabad', '431001', 11, 2),
(7, 'QuickSwap Center', '101 Powai Street', 'Satara', '415001', 20, 5),
(8, 'Rapid EV Swap', '7 Vishrambaug', 'Sangli', '416416', 0, 0),
(9, 'UrbanCharge Point', '99 Station Road', 'Solapur', '413001', 4, 0),
(13, 'vedant jadhav', 'miraj', 'kupwad', '416436', 30, 2);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `role` enum('user','admin') DEFAULT 'user'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `role`) VALUES
(2, 'vedant', 'vsjadhav1085@gmail.com', 'scrypt:32768:8:1$rxmkMFug73EMN1Ee$707b1c10984f75df07cf25fc622440a7a6441513b71bb7f19825ca6b234e692300e881b19f4b8b8f78ee48b2dd3122fee27f37520f2760c8e3c3818e48798e57', 'admin'),
(3, 'suraj', 'suraj.upadhye@gmail.com', 'scrypt:32768:8:1$Ee5tPmsf7WryVByE$8054d441743c11348a16a2c0a61bb90d6a2a320bdf3cc538b44f720c7a8ca9e2dff4fae2efcf833669957d46eefae008ffcfebcd138340b08d5a4e4d0e0c66c0', 'user'),
(4, 'Nitin', 'nitin123@gmail.com', 'scrypt:32768:8:1$xfyCdAPYbFJUlvwb$8e084d29a0df792b6ebd62db400d4ea36eb655759f1acf4709ec2a86e4cec424dcdfe891b9e17c7d3c9873635d07de34647dd40c3e49c37a2a714b214ff1f7d8', 'user'),
(5, 'shivam pawar', 'shivam1209@gmail.com', 'scrypt:32768:8:1$GOZFKKMfhcgmYImc$56302704d1286922cde8baf51ef6bbbfee8f8afcec469d2ea3ee0119ecbeeb404ab9406d3e363a08c1dd198452dbb65f499f3eba98707235284e1f4871d80a3a', 'user');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `appointments`
--
ALTER TABLE `appointments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `station_id` (`station_id`);

--
-- Indexes for table `feedback`
--
ALTER TABLE `feedback`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `stations`
--
ALTER TABLE `stations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `appointments`
--
ALTER TABLE `appointments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `feedback`
--
ALTER TABLE `feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `stations`
--
ALTER TABLE `stations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `appointments`
--
ALTER TABLE `appointments`
  ADD CONSTRAINT `appointments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `appointments_ibfk_2` FOREIGN KEY (`station_id`) REFERENCES `stations` (`id`);

--
-- Constraints for table `feedback`
--
ALTER TABLE `feedback`
  ADD CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
