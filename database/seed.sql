USE dataspaces_mvp;

INSERT INTO admins (id, name, email, password_hash) VALUES
(1, 'Administrador do Data Space', 'admin@dataspace.local',
 'scrypt:32768:8:1$eA5PD8ClZpGAlYwH$34c630161378517afb4ffeb4a67be5b7a421f24e98b6ddfa6a27c2afb76a87d4d027dbd6372ebe2cf2cf72a8864c665cda5f946c1f664007ad2d925d3ce81d96');

INSERT INTO organizations
    (id, name, cnpj, email, password_hash, did, sector, role, contact_name, description, status)
VALUES
(1, 'TransLog Brasil', '11222333000181', 'contato@translog.com.br',
 'scrypt:32768:8:1$497z5fQI4xjp4ObT$31ad627ca42b185ea4e6cb4633ed9a50c5d5d8c502e9ee1ce3fa7efd53854f4df93be9a0986d4e1ec4fef03e551505d0a533c61a04d0c8512f17222d0e8f54a8',
 'did:example:translog', 'logistics', 'both', 'Equipe TransLog',
 'Operadora logística com foco em entregas rodoviárias.', 'active'),
(2, 'CargaCerta Transportes', '44555666000181', 'contato@cargacerta.com.br',
 'scrypt:32768:8:1$noQHFBeyPlpKmxBv$608f24a9e4e8b8adac1da06e18f8a136f56c2a89e57070a12a6c848e241a583f5fe225c53d886456f6636776d6f2f83a77f8b2c5a8c3a3ec08cb7df04ca9b07a',
 'did:example:cargacerta', 'transport', 'both', 'Equipe CargaCerta',
 'Transportadora com frota própria de caminhões e vans.', 'active');

INSERT INTO verifiable_credentials
    (organization_id, issuer_did, subject_did, role_provider, role_consumer, expires_at)
VALUES
(1, 'did:example:dataspace-authority', 'did:example:translog', TRUE, TRUE, '2030-12-31'),
(2, 'did:example:dataspace-authority', 'did:example:cargacerta', TRUE, TRUE, '2030-12-31');

INSERT INTO apis (id, provider_org_id, name, slug, description) VALUES
(1, 1, 'API de entregas', 'entregas', 'Acompanhamento de entregas e rotas.'),
(2, 2, 'API de veículos', 'veiculos', 'Disponibilidade da frota de transporte.');

INSERT INTO plans (id, code, name, subscription_price_usd, request_price_usd, max_access_level) VALUES
(1, 'simple', 'Plano simples', 10.00, 0.50, 'basic'),
(2, 'premium', 'Plano premium', 25.00, 0.20, 'premium');

INSERT INTO deliveries
    (api_id, tracking_code, origin, destination, status, estimated_delivery, route_distance_km)
VALUES
(1, 'ENT-001', 'São Paulo', 'Campinas', 'Em trânsito', '2030-11-03', 98.50),
(1, 'ENT-002', 'Curitiba', 'Joinville', 'Em preparação', '2030-11-05', 132.00);

INSERT INTO vehicles
    (api_id, vehicle_code, vehicle_type, available, capacity_kg, current_location, next_available_date)
VALUES
(2, 'VEI-001', 'Caminhão', TRUE, 12000.00, 'São Paulo', '2030-11-02'),
(2, 'VEI-002', 'Van', FALSE, 1800.00, 'Curitiba', '2030-11-06');