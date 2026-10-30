CREATE DATABASE IF NOT EXISTS dataspaces_mvp;
USE dataspaces_mvp;

CREATE TABLE organizations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    did VARCHAR(180) NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE verifiable_credentials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id INT NOT NULL,
    issuer_did VARCHAR(180) NOT NULL,
    subject_did VARCHAR(180) NOT NULL,
    role_provider BOOLEAN NOT NULL DEFAULT FALSE,
    role_consumer BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

CREATE TABLE apis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider_org_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    slug VARCHAR(60) NOT NULL UNIQUE,
    description VARCHAR(255) NOT NULL,
    FOREIGN KEY (provider_org_id) REFERENCES organizations(id)
);

CREATE TABLE plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(80) NOT NULL,
    subscription_price_usd DECIMAL(10, 2) NOT NULL,
    request_price_usd DECIMAL(10, 2) NOT NULL,
    max_access_level VARCHAR(20) NOT NULL
);

CREATE TABLE subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    consumer_org_id INT NOT NULL,
    api_id INT NOT NULL,
    plan_id INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (consumer_org_id, api_id),
    FOREIGN KEY (consumer_org_id) REFERENCES organizations(id),
    FOREIGN KEY (api_id) REFERENCES apis(id),
    FOREIGN KEY (plan_id) REFERENCES plans(id)
);

CREATE TABLE deliveries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    api_id INT NOT NULL,
    tracking_code VARCHAR(40) NOT NULL,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    status VARCHAR(40) NOT NULL,
    estimated_delivery DATE NOT NULL,
    route_distance_km DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (api_id) REFERENCES apis(id)
);

CREATE TABLE vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    api_id INT NOT NULL,
    vehicle_code VARCHAR(40) NOT NULL,
    vehicle_type VARCHAR(60) NOT NULL,
    available BOOLEAN NOT NULL,
    capacity_kg DECIMAL(10, 2) NOT NULL,
    current_location VARCHAR(100) NOT NULL,
    next_available_date DATE NOT NULL,
    FOREIGN KEY (api_id) REFERENCES apis(id)
);

CREATE TABLE api_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subscription_id INT NOT NULL,
    access_level VARCHAR(20) NOT NULL,
    endpoint VARCHAR(120) NOT NULL,
    amount_usd DECIMAL(10, 2) NOT NULL,
    success BOOLEAN NOT NULL,
    error_message VARCHAR(255),
    requested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
);
