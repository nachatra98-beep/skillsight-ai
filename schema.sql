-- SkillSight AI Database Schema (MySQL 8.x Compatible)
-- Created for AI-Enabled Labour Market Intelligence and Skill Demand-Supply Forecasting Engine

CREATE DATABASE IF NOT EXISTS skillsight_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE skillsight_db;

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Learner', 'Analyst', 'Admin') DEFAULT 'Learner',
    region VARCHAR(100) DEFAULT 'Global',
    target_role VARCHAR(100) DEFAULT 'Software Developer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Skills taxonomy
CREATE TABLE IF NOT EXISTS skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,
    growth_rate DECIMAL(5,2) DEFAULT 0.00,
    demand_level ENUM('Very High', 'High', 'Moderate', 'Low', 'Declining') DEFAULT 'Moderate',
    is_outdated BOOLEAN DEFAULT FALSE,
    outdated_reason TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Courses catalog with Upskill / Outdated classification
CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    provider VARCHAR(150) NOT NULL,
    level ENUM('Beginner', 'Intermediate', 'Advanced') DEFAULT 'Beginner',
    duration VARCHAR(50) DEFAULT '4 Weeks',
    domain VARCHAR(100) NOT NULL,
    status ENUM('upskill', 'stable', 'outdated') DEFAULT 'upskill',
    relevance_score INT DEFAULT 85,
    key_reason TEXT,
    replacement_course VARCHAR(200) NULL,
    image_badge VARCHAR(50) DEFAULT 'icon-code',
    is_free BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Course to Skills mapping
CREATE TABLE IF NOT EXISTS course_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    skill_id INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

-- 5. Demand & Supply Timeseries data (Historical 24+ months)
CREATE TABLE IF NOT EXISTS demand_timeseries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    skill_id INT NOT NULL,
    region VARCHAR(100) DEFAULT 'Global',
    period_date DATE NOT NULL,
    demand_count INT NOT NULL,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS supply_timeseries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    skill_id INT NOT NULL,
    region VARCHAR(100) DEFAULT 'Global',
    period_date DATE NOT NULL,
    supply_count INT NOT NULL,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

-- 6. Forecasts table (Next 12-24 Months)
CREATE TABLE IF NOT EXISTS forecasts (
    forecast_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_id INT NOT NULL,
    type ENUM('demand', 'supply') NOT NULL,
    period_date DATE NOT NULL,
    predicted_value INT NOT NULL,
    lower_ci INT NOT NULL,
    upper_ci INT NOT NULL,
    model_name VARCHAR(50) DEFAULT 'Exponential Smoothing / ARIMA',
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

-- 7. Chat messages / Session storage
CREATE TABLE IF NOT EXISTS chat_messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    sender ENUM('user', 'bot') NOT NULL,
    message TEXT NOT NULL,
    intent VARCHAR(50) DEFAULT 'general',
    rating INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
