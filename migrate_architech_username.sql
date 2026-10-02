-- Run once, after backup and review, before deploying the new bot code.
-- Renaming the row keeps its id and all messages.client_id references unchanged.
BEGIN;
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM clients WHERE username = 'architechlaboratory')
       AND EXISTS (SELECT 1 FROM clients WHERE username = 'architechsystems') THEN
        RAISE EXCEPTION 'Both Architech usernames exist: inspect client IDs and messages before migration';
    END IF;

    UPDATE clients SET username = 'architechsystems'
    WHERE username = 'architechlaboratory';
END $$;
COMMIT;