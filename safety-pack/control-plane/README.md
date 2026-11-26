# Safety Pack Control Plane — foundation slice

This is the first isolated control-plane foundation. It does not replace or
silently modify the existing Redis-backed Gateway.

## Included
- PostgreSQL schema for tenants, members, roles, API keys, policies,
  moderation events, decisions, and audit events.
- Tenant-scoped foreign keys and PostgreSQL Row-Level Security (RLS).
- Dependency-free API-key issuance and HMAC-SHA256 digest verification.
- Unit tests for key generation, malformed input, wrong secrets, and digest comparison.

## Security contract
1. Return the raw API key only at issuance. Persist prefix and digest, never raw_key.
2. SAFETY_API_KEY_PEPPER is an external secret of at least 32 characters. Never commit it.
3. The resolver must read only safety_api_key_auth_lookup to map a presented
   key digest to tenant_id/scopes before tenant context exists. Grant that role
   SELECT on this narrow lookup table only; it must not read customer content.
   Keep lookup rows synchronized with key creation/revocation in one transaction.
4. Every tenant-scoped DB transaction must set SET LOCAL app.tenant_id to the
   authenticated tenant UUID.
5. Use a non-owner runtime DB role without BYPASSRLS; keep migration and runtime roles separate.
6. Never put message text, images, biometric data, API keys, or bearer tokens in
   audit metadata or logs. Event rows store digest and length, not submitted content.
7. A client-supplied tenant ID is not authentication. Resolve tenant identity
   from a verified API key or member session.

## Apply and test
Apply migrations/0001_initial.sql with a dedicated migration role against an
empty PostgreSQL database. Then run:
python -m unittest discover -s tests -v

## Not implemented yet
No FastAPI routes, Gateway integration, DB pool, migration runner, member
login/session flow, RBAC enforcement, key rotation endpoint, audit writer, or
PostgreSQL RLS integration test. No deployment, release, GHCR publish, pilot,
or production-data access.
