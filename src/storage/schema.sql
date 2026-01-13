-- MariaDB schema for Air Quality Agent
-- This script is executed on first container start via docker-entrypoint-initdb.d

CREATE TABLE IF NOT EXISTS installations (
  installation_id INT NOT NULL,
  name VARCHAR(255) NULL,
  lat DECIMAL(10,7) NULL,
  lng DECIMAL(10,7) NULL,
  address VARCHAR(255) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (installation_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS measurements (
  id BIGINT NOT NULL AUTO_INCREMENT,
  installation_id INT NOT NULL,
  measured_at DATETIME NOT NULL,
  param VARCHAR(64) NOT NULL,
  value DECIMAL(12,4) NULL,
  source VARCHAR(64) NOT NULL DEFAULT 'airly',
  from_datetime DATETIME NULL,
  till_datetime DATETIME NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_measurement (installation_id, measured_at, param),
  KEY idx_installation_time (installation_id, measured_at),
  KEY idx_param_time (param, measured_at)
) ENGINE=InnoDB;
