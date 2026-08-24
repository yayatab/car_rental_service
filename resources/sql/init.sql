-- Initialize Database for Car Rental Service (DriveNow)

CREATE DATABASE IF NOT EXISTS `rental_service`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE `rental_service`;

-- for clean re-initialization, drop if exists.
DROP TABLE IF EXISTS `rentals`;
DROP TABLE IF EXISTS `cars`;

-- 1. Cars Table
-- Manages vehicle fleet, details, and current operational status
CREATE TABLE `cars` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `model` VARCHAR(255) NOT NULL,
    `year` INT NOT NULL,
    `status` ENUM('AVAILABLE', 'IN_USE', 'UNDER_MAINTENANCE') NOT NULL DEFAULT 'AVAILABLE',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_cars_status` (`status`),
    INDEX `idx_cars_model` (`model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Rentals Table
-- Tracks vehicle rental transactions, customer information, and rental timeframes
CREATE TABLE `rentals` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `car_id` INT NOT NULL,
    `customer_name` VARCHAR(255) NOT NULL,
    `start_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `end_date` DATETIME NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_rentals_car`
        FOREIGN KEY (`car_id`) REFERENCES `cars` (`id`)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    INDEX `idx_rentals_car_id` (`car_id`),
    INDEX `idx_rentals_customer_name` (`customer_name`),
    INDEX `idx_rentals_dates` (`start_date`, `end_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `cars` (`model`, `year`, `status`) VALUES
    ('Toyota Corolla', 2022, 'AVAILABLE'),
    ('Hyundai Ioniq 5', 2023, 'AVAILABLE'),
    ('Tesla Model 3', 2024, 'IN_USE'),
    ('Mazda 3', 2021, 'UNDER_MAINTENANCE');

INSERT INTO `rentals` (`car_id`, `customer_name`, `start_date`, `end_date`) VALUES
    (3, 'Alice Johnson', NOW() - INTERVAL 2 DAY, NULL);
