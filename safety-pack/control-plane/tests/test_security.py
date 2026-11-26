import unittest
from security import hash_api_key, issue_api_key, verify_api_key

PEPPER = "test-only-pepper-value-with-at-least-32-characters"

class ApiKeyTests(unittest.TestCase):
    def test_issue_returns_raw_once_and_digest_is_not_raw(self):
        issued = issue_api_key(PEPPER)
        self.assertTrue(issued.raw_key.startswith("spk_"))
        self.assertEqual(len(issued.digest), 64)
        self.assertNotIn(issued.raw_key, issued.digest)
        self.assertTrue(verify_api_key(issued.raw_key, issued.digest, PEPPER))

    def test_each_issued_key_is_unique(self):
        first, second = issue_api_key(PEPPER), issue_api_key(PEPPER)
        self.assertNotEqual(first.raw_key, second.raw_key)
        self.assertNotEqual(first.digest, second.digest)

    def test_wrong_key_and_pepper_fail(self):
        issued = issue_api_key(PEPPER)
        self.assertFalse(verify_api_key("spk_wrong.secret", issued.digest, PEPPER))
        self.assertFalse(verify_api_key(issued.raw_key, issued.digest, "another-pepper-value-with-32-chars"))

    def test_malformed_inputs_fail_closed(self):
        self.assertFalse(verify_api_key("", "0" * 64, PEPPER))
        self.assertFalse(verify_api_key("spk_bad", "short", PEPPER))
        with self.assertRaises(ValueError):
            issue_api_key("short")

    def test_hash_is_deterministic(self):
        issued = issue_api_key(PEPPER)
        self.assertEqual(hash_api_key(issued.raw_key, PEPPER), issued.digest)

if __name__ == "__main__":
    unittest.main()
