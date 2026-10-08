-- Apply to the shared Railway Postgres database before deploying the portal endpoint.
-- Requires the clients table to exist. Safe to rerun when the table is absent or already migrated.
BEGIN;

CREATE TABLE IF NOT EXISTS chat_modes (
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    phone VARCHAR(50) NOT NULL,
    mode VARCHAR(20) NOT NULL DEFAULT 'ai' CHECK (mode IN ('ai', 'human')),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (client_id, phone)
);

-- Accommodate the earlier schema.sql definition if chat_modes already exists.
ALTER TABLE chat_modes ALTER COLUMN mode TYPE VARCHAR(20);
ALTER TABLE chat_modes ALTER COLUMN mode SET DEFAULT 'ai';
ALTER TABLE chat_modes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE chat_modes ALTER COLUMN updated_at SET DEFAULT NOW();

CREATE INDEX IF NOT EXISTS idx_chat_modes_client_phone
    ON chat_modes(client_id, phone);

COMMIT;