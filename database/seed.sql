USE dataspaces_mvp;

INSERT INTO organizations (id, name, did) VALUES
(1, 'TransLog Brasil', 'did:example:translog'),
(2, 'CargaCerta Transportes', 'did:example:cargacerta');

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