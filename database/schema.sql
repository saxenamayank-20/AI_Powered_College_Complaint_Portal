-- ============================================
-- College Complaint Portal - Database Schema
-- ============================================

CREATE DATABASE IF NOT EXISTS college_complaint_portal;
USE college_complaint_portal;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin') DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Complaints / Tickets Table
CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id VARCHAR(30) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    complaint_text TEXT NOT NULL,
    category VARCHAR(50),
    priority ENUM('Low', 'Medium', 'High') DEFAULT 'Low',
    summary VARCHAR(255),
    status ENUM('Pending', 'In Progress', 'Resolved') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert default admin
INSERT INTO users (name, email, password, role)
VALUES ('Admin', 'admin@college.com', '$2b$12$KIXaB0zqZ5Q1e1e1e1e1eOQKIXaB0zqZ5Q1e1e1e1e1eOQKIXaB0z', 'admin')
ON DUPLICATE KEY UPDATE id=id;
