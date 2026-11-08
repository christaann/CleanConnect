-- ============================================================
-- CleanConnect Database Setup — Updated with User Login System
-- Run this entire file in MySQL Workbench (File > Open SQL Script)
-- then click the lightning bolt to execute
-- ============================================================

CREATE DATABASE IF NOT EXISTS cleanconnect;
USE cleanconnect;

-- Drop tables in correct order (foreign key constraints)
DROP TABLE IF EXISTS complaints;
DROP TABLE IF EXISTS admin_users;
DROP TABLE IF EXISTS users;

-- ============================================================
-- TABLE 1: users
-- Stores registered citizen accounts
-- ============================================================
CREATE TABLE users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(150) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE 2: admin_users
-- Stores admin login credentials
-- ============================================================
CREATE TABLE admin_users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE 3: complaints
-- Now includes user_id as foreign key linking to users table
-- ============================================================
CREATE TABLE complaints (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT DEFAULT NULL,
    issue_type   VARCHAR(100) NOT NULL,
    location     VARCHAR(255) NOT NULL,
    latitude     DECIMAL(10,8) DEFAULT NULL,
    longitude    DECIMAL(11,8) DEFAULT NULL,
    description  TEXT,
    photo        VARCHAR(255) DEFAULT NULL,
    status       ENUM('Pending','In Progress','Resolved') DEFAULT 'Pending',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================
-- Admin account
-- Username : admin
-- Password : Admin@123
-- ============================================================
INSERT INTO admin_users (username, password)
VALUES ('admin', 'scrypt:32768:8:1$hOMzsIKwdgODSRRY$63b90597bd7ae00f2c9ddeecf230cf7623826d6bb6e375161ff78fcca358b6099309918cb8b79aa63c6ce54c191dc05944c0aa89fdda889853f43119d8b19e82');

-- ============================================================
-- Sample users for testing
-- Password for both sample users: Test@1234
-- ============================================================
INSERT INTO users (name, email, password) VALUES
('Rahul Sharma',  'rahul@example.com',  'scrypt:32768:8:1$IUOG8sqQgSCi8NUs$de2a7a7213d1780df472237ea3b35cad2ec12371653653da317d3a5946da988a5f833217b82309d3d5973f44f9c59e657bff98bbe6c2314e6792e3f846b7db73'),
('Priya Nair',    'priya@example.com',  'scrypt:32768:8:1$fW6ia5eGqvckCkUJ$d0ae4b8fafcf48e04d5dfb7ee7240a3226e9eda385cccb2db99a8278d9a8310ee17b2631d4e1baa87099ea1a1723ebfd2eecc01c82fc75d9fac5bd0504a69e21');

-- ============================================================
-- Sample complaints linked to users
-- ============================================================
INSERT INTO complaints (user_id, issue_type, location, latitude, longitude, description, status) VALUES
(1, 'Garbage',                  'MG Road, Bengaluru',               12.97160, 77.59460, 'Large pile of garbage near the bus stop not cleared for 3 days.', 'Pending'),
(1, 'Water Leakage',            'Koramangala 5th Block, Bengaluru',  12.93520, 77.62450, 'Water pipe burst near the signal, water flowing on road.', 'In Progress'),
(2, 'Street Light Not Working', 'Indiranagar 100 Feet Road',        12.97840, 77.64080, 'Three street lights not working for the past week.', 'Resolved'),
(2, 'Road Damage',              'Whitefield Main Road, Bengaluru',   12.96980, 77.75000, 'Large pothole in the middle of the road.', 'Pending'),
(1, 'Drainage Blockage',        'Jayanagar 4th Block, Bengaluru',    12.92500, 77.59380, 'Drain blocked causing water logging during rain.', 'In Progress'),
(2, 'Garbage',                  'Malleshwaram Circle, Bengaluru',    13.00350, 77.57100, 'Garbage bin overflowing, waste spread on footpath.', 'Resolved'),
(1, 'Street Light Not Working', 'BTM Layout 2nd Stage, Bengaluru',   12.91660, 77.61010, 'Entire street dark at night.', 'Pending'),
(2, 'Road Damage',              'Hebbal Flyover Area, Bengaluru',    13.03580, 77.59700, 'Cracks developing on the service road.', 'In Progress');

-- Verify
SELECT 'users' AS table_name, COUNT(*) AS rows FROM users
UNION ALL SELECT 'admin_users', COUNT(*) FROM admin_users
UNION ALL SELECT 'complaints',  COUNT(*) FROM complaints;

-- ============================================================
-- ADMIN LOGIN  : username=admin      password=Admin@123
-- USER LOGIN   : email=rahul@example.com  password=Test@1234
-- USER LOGIN   : email=priya@example.com  password=Test@1234
-- If admin login fails visit: http://localhost:5000/setup_admin
-- ============================================================