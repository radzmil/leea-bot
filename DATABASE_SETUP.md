# Railway PostgreSQL

This repository contains the `leea-bot` Flask service. The `portal` directory
in this workspace contains no application code, so the Railway `web` service
cannot be configured or tested from this repository.

1. Rotate the Postgres password in Railway (a credential was exposed in chat).
   Check for any other services using the old credential and redeploy them.
2. In Railway, set `DATABASE_URL` in **leea-bot → Variables** to a variable
   reference to **Postgres → DATABASE_URL** (`${{Postgres.DATABASE_URL}}`).
   Do the same in **web → Variables** if web needs database access. Never put
   the database URL itself in Git. The internal hostname is only accessible
   from services inside the Railway project/network, not from a local laptop.
3. Run `schema.sql` using Railway's Postgres SQL interface or a Railway shell
   with database access. Inspect any existing `clients` and `messages` tables
   before running it: `CREATE TABLE IF NOT EXISTS` does not reconcile different
   pre-existing column definitions. If an existing `clients` row has username
   `architechlaboratory`, back up the database and run
   `migrate_architech_username.sql` **before** `schema.sql` and before deploying
   the new bot code. If both old and new usernames exist, the migration stops:
   inspect their IDs and messages instead of merging them blindly.
4. Redeploy the bot and verify in its logs that a test chat is saved. Check
   `SELECT id, username FROM clients ORDER BY id;` and
   `SELECT client_id, sender, prospect_phone FROM messages ORDER BY id DESC LIMIT 10;`.

The bot already depends on `psycopg2-binary` in `requirements.txt`. The `web`
service must install a PostgreSQL driver appropriate for its **own** language;
its source and dependency manifest are not present here. Sharing one Postgres
database does not automatically register SBLeisure: the current bot code has
`architechsystems` and `aluzlia` configured. `aluzlia` is not assumed to be
SBLeisure; its mapping must be confirmed before changing it.

Confirmed business identities: SBLeisure / Zulfa has client reference
`CLI-1000`; Architech Systems / LeeA has `CLI-1001`. The WhatsApp tenant
username for SBLeisure is still unconfirmed. Do not rename `aluzlia`, insert
an assumed SBLeisure username, or route Zulfa traffic through LeeA solely
based on these business references.

Reserved business client references (not yet assigned): `CLI-1002` and
`CLI-1003`. Client names, bot identities and tenant usernames have not been
provided. These reservations are documentation only: they do not create
`clients` rows, enable webhooks, or allocate PostgreSQL primary keys. Confirm
each identity and username before provisioning or routing either client.

Architech Systems / LeeA uses tenant username `architechsystems` and business
client reference `CLI-1001` (currently the default in `leea_brain.py`). This
reference is **not** the numeric primary key `clients.id` used by
`messages.client_id`. Never force the database row ID to `1001` to match it.

The default `/webhook` route remains the LeeA bot route; the app's internal
tenant ID is now `architechsystems`. Check any external integrations that send
or request tenant-specific URLs or use the former tenant username.