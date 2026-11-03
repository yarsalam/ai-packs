from pathlib import Path
import re


WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"


def test_public_publish_paths_are_disabled_until_release_go():
    workflow_files = sorted(WORKFLOWS.glob("*.yml"))
    assert workflow_files, "expected GitHub Actions workflow files"

    forbidden = {
        "packages: write": re.compile(r"(?m)^\s*packages:\s*write\s*$"),
        "Docker registry login": re.compile(r"docker/login-action@"),
        "Buildx push": re.compile(r"(?m)^\s*--push\s*$"),
        "docker push": re.compile(r"(?m)^\s*run:\s*docker\s+push\b"),
        "GitHub Release upload": re.compile(r"softprops/action-gh-release@"),
        "published release trigger": re.compile(r"(?m)^\s{2}release:\s*$"),
    }

    for workflow in workflow_files:
        content = workflow.read_text(encoding="utf-8")
        for label, pattern in forbidden.items():
            assert not pattern.search(content), f"{workflow.name} contains forbidden {label}"
