from pathlib import Path
import unittest

MIGRATION = Path(__file__).parents[1] / "migrations" / "0001_initial.sql"


class SchemaContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = MIGRATION.read_text(encoding="utf-8")

    def test_required_control_plane_entities_exist(self):
        for table in (
            "safety_tenants", "safety_tenant_members", "safety_api_keys",
            "safety_api_key_auth_lookup", "safety_policies",
            "safety_moderation_events", "safety_moderation_decisions",
            "safety_audit_events",
        ):
            with self.subTest(table=table):
                self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", self.sql)

    def test_tenant_owned_tables_have_forced_rls(self):
        for table in (
            "safety_tenant_members", "safety_api_keys", "safety_policies",
            "safety_moderation_events", "safety_moderation_decisions",
            "safety_audit_events",
        ):
            with self.subTest(table=table):
                self.assertIn(f"'{table}'", self.sql)
        self.assertIn("ENABLE ROW LEVEL SECURITY", self.sql)
        self.assertIn("FORCE ROW LEVEL SECURITY", self.sql)
        self.assertIn("current_setting(''app.tenant_id'',true)", self.sql)

    def test_api_key_storage_is_digest_only(self):
        self.assertIn("key_hash CHAR(64) NOT NULL", self.sql)
        self.assertNotIn("raw_key TEXT", self.sql)
        self.assertNotIn("api_key TEXT", self.sql)

    def test_event_schema_does_not_store_submitted_text(self):
        self.assertIn("content_sha256 CHAR(64)", self.sql)
        self.assertIn("content_length INTEGER", self.sql)
        self.assertNotIn("message_text TEXT", self.sql)
        self.assertNotIn("raw_content TEXT", self.sql)


if __name__ == "__main__":
    unittest.main()
