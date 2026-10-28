#!/usr/bin/env python3
"""Validate generated AI Pack distributions without starting inference containers."""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

PACKS = ("seo-pack", "safety-pack", "revenue-pack", "matching-pack")


def fail(message: str) -> None:
    raise SystemExit("distribution validation failed: " + message)


def validate_pack(dist_root: Path, pack_name: str) -> dict:
    pack = dist_root / pack_name
    if not pack.is_dir():
        fail(f"missing folder: {pack}")
    for required in ("compose.yaml", ".env.example", "README.md", "manifest.json", "gateway/Dockerfile", "gateway/main.py"):
        if not (pack / required).is_file():
            fail(f"{pack_name}: missing {required}")

    compose_path = pack / "compose.yaml"
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    services = compose.get("services", {})
    volumes = compose.get("volumes", {})
    if "gateway" not in services or "redis" not in services:
        fail(f"{pack_name}: gateway or redis service missing")
    gateway_ports = services["gateway"].get("ports", [])
    if not any(str(p).startswith("127.0.0.1:") for p in gateway_ports):
        fail(f"{pack_name}: gateway must bind to loopback by default")

    for service_name, service in services.items():
        context = service.get("build", {}).get("context")
        if context:
            resolved = (pack / context).resolve()
            if not resolved.is_dir():
                fail(f"{pack_name}/{service_name}: build context missing: {context}")
            if not resolved.is_relative_to(pack.resolve()):
                fail(f"{pack_name}/{service_name}: build context escapes the distribution")
            if not (resolved / "Dockerfile").is_file():
                fail(f"{pack_name}/{service_name}: Dockerfile missing in {context}")
        if "container_name" in service:
            fail(f"{pack_name}/{service_name}: hard-coded container_name prevents safe composition")
        for dependency in (service.get("depends_on") or {}):
            if dependency not in services:
                fail(f"{pack_name}/{service_name}: unknown dependency {dependency}")
        for mount in service.get("volumes", []) or []:
            source = str(mount).split(":", 1)[0]
            if source and not source.startswith((".", "/", "$")) and source not in volumes:
                fail(f"{pack_name}/{service_name}: undeclared named volume {source}")

    # All Python source files included in a distribution must remain local.
    for relative in ("services",):
        folder = pack / relative
        if not folder.is_dir():
            fail(f"{pack_name}: missing {relative}")
        for source in folder.rglob("*.py"):
            text = source.read_text(encoding="utf-8", errors="replace")
            if "../../python-ai/services" in text:
                fail(f"{pack_name}: source still references monorepo path: {source.relative_to(pack)}")

    return {
        "pack": pack_name,
        "services": list(services),
        "build_contexts": sum(1 for service in services.values() if service.get("build")),
        "compose": str(compose_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.dist_dir.resolve()
    results = [validate_pack(root, name) for name in PACKS]
    for plugin_archive in ("seo-pack-wordpress.zip", "safety-pack-wordpress.zip", "revenue-pack-wordpress.zip", "matching-pack-wordpress.zip"):
        if not (root / plugin_archive).is_file():
            fail(f"missing plugin archive {plugin_archive}")
    for pack_archive in PACKS:
        if not (root / f"{pack_archive}.zip").is_file():
            fail(f"missing pack archive {pack_archive}.zip")
    print(yaml.safe_dump({"status": "ok", "packs": results}, sort_keys=False))


if __name__ == "__main__":
    main()
