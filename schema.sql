-- Run against the Railway Postgres database before enabling chat persistence.
-- Existing rows are preserved. Review existing schemas before applying changes.
BEGIN;

CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE
);

ALTER TABLE clients ADD COLUMN IF NOT EXISTS token_balance BIGINT NOT NULL DEFAULT 0;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS token_quota BIGINT NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    client_id INTEGER,
    sender VARCHAR(50),
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE messages ADD COLUMN IF NOT EXISTS prospect_phone VARCHAR(50);

CREATE INDEX IF NOT EXISTS messages_client_prospect_id_idx
    ON messages (client_id, prospect_phone, id DESC);

CREATE TABLE IF NOT EXISTS prospect_contacts (
    client_id INTEGER NOT NULL REFERENCES clients(id),
    phone VARCHAR(50) NOT NULL,
    name VARCHAR(150) NOT NULL,
    source VARCHAR(10) NOT NULL CHECK (source IN ('auto', 'manual')),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (client_id, phone)
);

CREATE TABLE IF NOT EXISTS chat_modes (
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    phone VARCHAR(50) NOT NULL,
    mode VARCHAR(20) NOT NULL DEFAULT 'ai' CHECK (mode IN ('ai', 'human')),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (client_id, phone)
);

CREATE INDEX IF NOT EXISTS idx_chat_modes_client_phone
    ON chat_modes(client_id, phone);

CREATE TABLE IF NOT EXISTS whatsapp_inbound_claims (
    tenant VARCHAR(100) NOT NULL,
    message_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (tenant, message_id)
);

COMMIT;

-- Known usernames in this bot repository. Do not assume aluzlia is SBLeisure.
-- If production already has the legacy username, run migrate_architech_username.sql
-- first so existing messages retain their client_id.
INSERT INTO clients (username) VALUES ('architechsystems'), ('aluzlia')
ON CONFLICT (username) DO NOTHING;

-- Add each real bot username after confirming its identity, e.g.:
-- INSERT INTO clients (username) VALUES ('actual_username')
-- ON CONFLICT (username) DO NOTHING;
-- Verify with: SELECT id, username FROM clients ORDER BY id;