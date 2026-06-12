CREATE DATABASE weather_pipeline;

USE weather_pipeline;

CREATE TABLE cities (
    city_id INT AUTO_INCREMENT PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6)
);

CREATE TABLE weather_data (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    city_id INT,
    timestamp DATETIME,
    temperature_c DECIMAL(5,2),
    humidity INT,
    pressure_hpa DECIMAL(7,2),
    wind_speed_mps DECIMAL(5,2),
    weather_condition VARCHAR(100),
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

CREATE TABLE pipeline_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    run_time DATETIME,
    status VARCHAR(50),
    records_processed INT,
    message TEXT
);