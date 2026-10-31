from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai_pack_control_agent as agent  # noqa: E402


class AiPackControlAgentTests(unittest.TestCase):
    def test_only_four_fixed_projects_are_allowlisted(self) -> None:
        self.assertEqual(set(agent.PACKS), {
            "matching-pack", "seo-pack", "revenue-pack", "safety-pack"
        })
        self.assertNotIn("mobapp", agent.PACKS)
        self.assertNotIn("admin", agent.PACKS)

    def test_unknown_pack_cannot_build_compose_command(self) -> None:
        with self.assertRaises(KeyError):
            agent.base("mobapp")

    def test_compose_command_uses_fixed_project_and_paths(self) -> None:
        with patch.object(agent, "ROOT", Path("/test/root")), \
             patch.object(agent, "ENV_DIR", Path("/test/env")), \
             patch.object(Path, "is_file", return_value=True):
            args = agent.base("seo-pack")
        self.assertIn("yarsalam-seo-pack", args)
        self.assertIn("/test/root/deploy/compose/seo-pack.json", args)
        self.assertIn("/test/env/seo-pack.env", args)

    def test_stop_targets_only_compose_stop(self) -> None:
        with patch.object(agent, "ROOT", Path("/tmp")), \
             patch.object(agent, "ENV_DIR", Path("/tmp")), \
             patch.object(Path, "is_file", return_value=True), \
             patch.object(agent, "run", return_value=type("Result", (), {
                 "returncode": 0, "stderr": ""
             })()) as call:
            result = agent.stop_pack("seo-pack")
        self.assertTrue(result["ok"])
        command = call.call_args.args[0]
        self.assertEqual(command[-1], "stop")
        self.assertNotIn("down", command)
        self.assertNotIn("--remove-orphans", command)
        self.assertNotIn("-v", command)

    def test_preflight_refuses_latest_image(self) -> None:
        with patch.object(agent, "base", return_value=["docker", "compose"]), \
             patch.object(agent, "run") as call:
            call.side_effect = [
                type("Result", (), {"returncode": 0, "stdout": "gateway\n"})(),
                type("Result", (), {"returncode": 0,
                    "stdout": "ghcr.io/yarsalam/ai-packs/seo-pack-gateway:latest\n"})(),
            ]
            result = agent.preflight("seo-pack")
        self.assertFalse(result["ready"])
        self.assertIn("non-immutable", result["reason"])

    def test_preflight_missing_immutable_image_never_pulls(self) -> None:
        image = "ghcr.io/yarsalam/ai-packs/seo-pack-gateway:sha-" + "a" * 40
        with patch.object(agent, "base", return_value=["docker", "compose"]), \
             patch.object(agent, "read_env", return_value={"SEO_PACK_ADMIN_TOKEN": "x" * 64}), \
             patch.object(agent, "run") as call:
            call.side_effect = [
                type("Result", (), {"returncode": 0, "stdout": "gateway\n"})(),
                type("Result", (), {"returncode": 0, "stdout": image + "\n"})(),
                type("Result", (), {"returncode": 1, "stderr": "not found"})(),
            ]
            result = agent.preflight("seo-pack")
        self.assertFalse(result["ready"])
        self.assertIn(image, result["missing_images"])
        self.assertTrue(all("pull" not in str(c.args[0]) for c in call.call_args_list))


if __name__ == "__main__":
    unittest.main()
