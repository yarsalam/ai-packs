-- Safety Pack control-plane foundation.
-- Apply with a PostgreSQL migration runner as a role that owns these objects.
-- Application transactions MUST execute SET LOCAL app.tenant_id = '<authenticated tenant UUID>'
-- before touching tenant-scoped tables. RLS is defense in depth.
BEGIN;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE IF NOT EXISTS safety_tenants (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 slug TEXT NOT NULL UNIQUE,
 display_name TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','suspended','closed')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS safety_tenant_members (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 tenant_id UUID NOT NULL REFERENCES safety_tenants(id) ON DELETE CASCADE,
 email TEXT NOT NULL,
 role TEXT NOT NULL CHECK (role IN ('owner','admin','reviewer','analyst')),
 status TEXT NOT NULL DEFAULT 'invited' CHECK (status IN ('invited','active','disabled')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 UNIQUE (tenant_id,email), UNIQUE (tenant_id,id)
);
CREATE TABLE IF NOT EXISTS safety_api_keys (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 tenant_id UUID NOT NULL REFERENCES safety_tenants(id) ON DELETE CASCADE,
 name TEXT NOT NULL, key_prefix TEXT NOT NULL, key_hash CHAR(64) NOT NULL,
 scopes TEXT[] NOT NULL DEFAULT ARRAY['moderation:write']::TEXT[],
 status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','revoked')),
 expires_at TIMESTAMPTZ, last_used_at TIMESTAMPTZ,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(), revoked_at TIMESTAMPTZ,
 UNIQUE (key_hash), UNIQUE (tenant_id,id)
);
CREATE INDEX IF NOT EXISTS safety_api_keys_tenant_status_idx ON safety_api_keys(tenant_id,status);
-- Narrow bootstrap lookup used before tenant context is known.
-- Grant SELECT on this table only to the API-key resolver DB role; never expose
-- it through tenant-facing CRUD endpoints. It contains only key metadata/hash.
CREATE TABLE IF NOT EXISTS safety_api_key_auth_lookup (
 key_hash CHAR(64) PRIMARY KEY,
 tenant_id UUID NOT NULL,
 api_key_id UUID NOT NULL,
 scopes TEXT[] NOT NULL,
 status TEXT NOT NULL CHECK (status IN ('active','revoked')),
 expires_at TIMESTAMPTZ,
 FOREIGN KEY (tenant_id,api_key_id)
   REFERENCES safety_api_keys(tenant_id,id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS safety_api_key_lookup_tenant_idx
 ON safety_api_key_auth_lookup(tenant_id);
CREATE TABLE IF NOT EXISTS safety_policies (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 tenant_id UUID NOT NULL REFERENCES safety_tenants(id) ON DELETE CASCADE,
 version INTEGER NOT NULL CHECK (version > 0),
 state TEXT NOT NULL DEFAULT 'draft' CHECK (state IN ('draft','active','archived')),
 policy JSONB NOT NULL, created_by UUID, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 UNIQUE (tenant_id,version), UNIQUE (tenant_id,id),
 FOREIGN KEY (tenant_id,created_by) REFERENCES safety_tenant_members(tenant_id,id)
);
CREATE UNIQUE INDEX IF NOT EXISTS safety_policies_one_active_per_tenant ON safety_policies(tenant_id) WHERE state='active';
CREATE TABLE IF NOT EXISTS safety_moderation_events (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 tenant_id UUID NOT NULL REFERENCES safety_tenants(id) ON DELETE CASCADE,
 external_reference TEXT, content_sha256 CHAR(64),
 content_length INTEGER NOT NULL CHECK (content_length >= 0),
 content_type TEXT NOT NULL CHECK (content_type IN ('text','comment','message','profile')),
 status TEXT NOT NULL DEFAULT 'received' CHECK (status IN ('received','decided','review','closed','failed')),
 received_at TIMESTAMPTZ NOT NULL DEFAULT now(), UNIQUE (tenant_id,id)
);
CREATE INDEX IF NOT EXISTS safety_events_tenant_received_idx ON safety_moderation_events(tenant_id,received_at DESC);
CREATE INDEX IF NOT EXISTS safety_events_tenant_external_ref_idx ON safety_moderation_events(tenant_id,external_reference) WHERE external_reference IS NOT NULL;
CREATE TABLE IF NOT EXISTS safety_moderation_decisions (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id UUID NOT NULL, event_id UUID NOT NULL,
 policy_id UUID, action TEXT NOT NULL CHECK (action IN ('allow','review','restrict','defer')),
 category TEXT NOT NULL, policy_version INTEGER,
 signal_metadata JSONB NOT NULL DEFAULT '{}'::jsonb, decided_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 FOREIGN KEY (tenant_id,event_id) REFERENCES safety_moderation_events(tenant_id,id) ON DELETE CASCADE,
 FOREIGN KEY (tenant_id,policy_id) REFERENCES safety_policies(tenant_id,id)
);
CREATE INDEX IF NOT EXISTS safety_decisions_tenant_event_idx ON safety_moderation_decisions(tenant_id,event_id,decided_at DESC);
CREATE TABLE IF NOT EXISTS safety_audit_events (
 id BIGSERIAL PRIMARY KEY, tenant_id UUID NOT NULL REFERENCES safety_tenants(id) ON DELETE CASCADE,
 actor_member_id UUID, action TEXT NOT NULL, resource_type TEXT NOT NULL, resource_id UUID,
 request_id TEXT, metadata JSONB NOT NULL DEFAULT '{}'::jsonb, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 FOREIGN KEY (tenant_id,actor_member_id) REFERENCES safety_tenant_members(tenant_id,id)
);
CREATE INDEX IF NOT EXISTS safety_audit_tenant_created_idx ON safety_audit_events(tenant_id,created_at DESC);
DO $$
DECLARE table_name TEXT;
BEGIN
 FOREACH table_name IN ARRAY ARRAY['safety_tenant_members','safety_api_keys','safety_policies','safety_moderation_events','safety_moderation_decisions','safety_audit_events'] LOOP
  EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY',table_name);
  EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY',table_name);
  EXECUTE format('DROP POLICY IF EXISTS tenant_isolation ON %I',table_name);
  EXECUTE format('CREATE POLICY tenant_isolation ON %I USING (tenant_id = NULLIF(current_setting(''app.tenant_id'',true),'''')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting(''app.tenant_id'',true),'''')::uuid)',table_name);
 END LOOP;
END $$;
COMMIT;
