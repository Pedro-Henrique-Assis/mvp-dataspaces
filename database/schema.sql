CREATE DATABASE IF NOT EXISTS dataspaces_mvp
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dataspaces_mvp;

CREATE TABLE organizations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    cnpj CHAR(14) NOT NULL UNIQUE,
    email VARCHAR(160) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    did VARCHAR(180) NOT NULL UNIQUE,
    sector VARCHAR(40) NOT NULL,
    role VARCHAR(10) NOT NULL,
    contact_name VARCHAR(120) NOT NULL,
    description VARCHAR(255),
    website VARCHAR(160),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    rejection_reason VARCHAR(255),
    credit_balance INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (credit_balance >= 0)
);

CREATE TABLE credit_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id INT NOT NULL,
    amount INT NOT NULL,
    type VARCHAR(20) NOT NULL,
    description VARCHAR(255) NOT NULL,
    balance_after INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE verifiable_credentials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id INT NOT NULL,
    issuer_did VARCHAR(180) NOT NULL,
    subject_did VARCHAR(180) NOT NULL,
    role_provider BOOLEAN NOT NULL DEFAULT FALSE,
    role_consumer BOOLEAN NOT NULL DEFAULT FALSE,
    issued_at DATE NOT NULL,
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
    basic_response TEXT NOT NULL,
    premium_response TEXT NOT NULL,
    policy_purpose VARCHAR(255) NOT NULL,
    policy_allows_redistribution BOOLEAN NOT NULL DEFAULT FALSE,
    policy_retention_days INT NOT NULL,
    policy_notes VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_org_id) REFERENCES organizations(id)
);

CREATE TABLE plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(80) NOT NULL,
    subscription_price_credits INT NOT NULL,
    request_price_credits INT NOT NULL,
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

CREATE TABLE api_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subscription_id INT NOT NULL,
    access_level VARCHAR(20) NOT NULL,
    endpoint VARCHAR(120) NOT NULL,
    credits INT NOT NULL,
    success BOOLEAN NOT NULL,
    error_message VARCHAR(255),
    requested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
);
