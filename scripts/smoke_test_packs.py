#!/usr/bin/env python3
"""Live smoke tests for already-running, locally built AI Pack distributions.

Uses only the Python standard library. It creates a short-lived test license
through each gateway, exercises one real inference route per pack, and revokes
the test license afterwards. Run only against a disposable/test deployment.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

PACKS: dict[str, dict[str, Any]] = {
    "seo-pack": {
        "port": 9000,
        "admin_env": "SEO_PACK_ADMIN_TOKEN",
        "tests": [
            {
                "name": "public website URL technical HTML audit",
                "method": "POST",
                "path": "/seo/audit/url",
                "payload": {"url": "https://example.com/"},
                "check": "url_audit",
            },
            {
                "name": "topical backlink similarity (embedding inference)",
                "method": "POST",
                "path": "/backlink/topic-similarity",
                "payload": {
                    "source_text": "راهنمای انتخاب کفش ورزشی مناسب برای دویدن",
                    "target_text": "نکات خرید کفش دویدن و تجهیزات ورزشی",
                },
                "check": "similarity",
            },
        ],
        "capability_gaps": [
            "Public internet-facing deployments need network-layer egress restrictions; application DNS checks alone cannot fully prevent DNS rebinding."
        ],
    },
    "safety-pack": {
        "port": 9001,
        "admin_env": "SAFETY_PACK_ADMIN_TOKEN",
        "tests": [
            {
                "name": "Persian safe-text moderation (semantic inference)",
                "method": "POST",
                "path": "/moderate/text",
                "payload": {"text": "سلام، برای استفاده از برنامه یک سؤال دارم.", "context": "message"},
                "check": "moderation",
            },
            {
                "name": "known-rule moderation case",
                "method": "POST",
                "path": "/moderate/text",
                "payload": {"text": "لطفاً آیدی تلگرام را بفرست", "context": "message"},
                "check": "blocked",
            },
        ],
        "capability_gaps": [],
    },
    "revenue-pack": {
        "port": 9002,
        "admin_env": "REVENUE_PACK_ADMIN_TOKEN",
        "tests": [
            {
                "name": "promotion scoring endpoint",
                "method": "POST",
                "path": "/monetization/predict-promotion",
                "payload": {
                    "user_id": 101,
                    "features": {
                        "engagement_score": 0.7,
                        "days_since_signup": 18,
                        "dismiss_rate": 0.1,
                        "last_purchase_days": 40,
                        "swipe_velocity": 3,
                        "avg_session_time": 240,
                        "promotion_ctr": 0.12,
                        "conversion_score": 0.45,
                        "hour_of_day": 15,
                        "is_weekend": 0,
                        "session_depth": 8,
                    },
                    "candidates": ["vip", "boost", "credit", "profile"],
                    "context": {"test": True},
                },
                "check": "promotion",
            },
        ],
        "capability_gaps": [
            "A successful promotion response does not prove the production model is trained or calibrated; the code can fall back to a rule-based score."
        ],
    },
    "matching-pack": {
        "port": 9003,
        "admin_env": "MATCHING_PACK_ADMIN_TOKEN",
        "tests": [
            {
                "name": "multilingual embedding inference",
                "method": "POST",
                "path": "/embed/text",
                "payload": {"text": "من به گفت‌وگوی محترمانه، صداقت و علایق مشترک اهمیت می‌دهم."},
                "check": "embedding",
            },
            {
                "name": "Persian sentiment model inference",
                "method": "POST",
                "path": "/personality/sentiment",
                "payload": {"messages": ["از آشنایی با شما خوشحالم.", "از این رفتار ناراحت شدم."]},
                "check": "sentiment",
            },
        ],
        "capability_gaps": [],
    },
}


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        values[key.strip()] = value
    return values


def request_json(
    base_url: str, path: str, method: str = "GET",
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None, timeout: float = 90,
) -> tuple[int, Any, int]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req_headers = {"Accept": "application/json"}
    if body is not None:
        req_headers["Content-Type"] = "application/json"
    req_headers.update(headers or {})
    req = urllib.request.Request(
        base_url.rstrip("/") + path, data=body, headers=req_headers, method=method
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read(2 * 1024 * 1024)
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read(2 * 1024 * 1024)
        status = exc.code
    elapsed_ms = int((time.monotonic() - started) * 1000)
    try:
        parsed: Any = json.loads(raw.decode("utf-8")) if raw else {}
    except (UnicodeDecodeError, json.JSONDecodeError):
        parsed = {"raw": raw[:400].decode("utf-8", errors="replace")}
    return status, parsed, elapsed_ms


def add_result(results: list[dict[str, Any]], name: str, ok: bool, status: int | None,
               elapsed_ms: int | None, detail: str) -> None:
    results.append({
        "test": name, "status": "PASS" if ok else "FAIL",
        "http_status": status, "duration_ms": elapsed_ms, "detail": detail,
    })


def validate_payload(check: str, response: Any) -> tuple[bool, str]:
    if not isinstance(response, dict):
        return False, "Expected a JSON object response"
    if check == "similarity":
        score = response.get("similarity")
        ok = isinstance(score, (int, float)) and math.isfinite(score) and -1 <= score <= 1
        return ok, f"similarity={score!r}; checks numeric cosine range [-1, 1]"
    if check == "url_audit":
        status_code = response.get("status_code")
        checks = response.get("checks")
        title = response.get("title")
        ok = (
            isinstance(status_code, int) and 200 <= status_code < 300
            and isinstance(title, str) and bool(title.strip())
            and isinstance(checks, list) and len(checks) >= 8
            and response.get("score_type") == "heuristic_on_page_checklist_not_google_ranking"
        )
        return ok, f"fetched_status={status_code!r}, title_present={bool(title)}, checks={len(checks) if isinstance(checks, list) else 'invalid'}"
    if check == "moderation":
        result = response.get("result", response)
        if not isinstance(result, dict) or not isinstance(result.get("allowed"), bool):
            return False, "Response has no boolean 'allowed' field"
        layer = result.get("layer")
        review = result.get("review_required", False)
        ok = result.get("allowed") is True and layer != "semantic_error" and not review
        return ok, f"allowed={result.get('allowed')!r}, layer={layer!r}, review_required={review!r}"
    if check == "blocked":
        ok = response.get("allowed") is False and response.get("reason") == "banned_keyword"
        return ok, f"allowed={response.get('allowed')!r}, reason={response.get('reason')!r}"
    if check == "promotion":
        variant, score = response.get("variant"), response.get("score")
        all_scores = response.get("all_scores")
        ok = (
            variant in {"vip", "boost", "credit", "profile"}
            and isinstance(score, (int, float)) and math.isfinite(score) and 0 <= score <= 1
            and isinstance(all_scores, list) and len(all_scores) == 4
        )
        return ok, f"variant={variant!r}, score={score!r}, candidates_scored={len(all_scores) if isinstance(all_scores, list) else 'invalid'}"
    if check == "embedding":
        embedding = response.get("embedding")
        dimension = response.get("dimension")
        ok = (
            isinstance(embedding, list) and len(embedding) > 0
            and isinstance(dimension, int) and dimension == len(embedding)
            and all(isinstance(x, (int, float)) and math.isfinite(x) for x in embedding)
        )
        return ok, f"dimension={dimension!r}, vector_length={len(embedding) if isinstance(embedding, list) else 'invalid'}"
    if check == "sentiment":
        predictions = response.get("sentiments")
        ok = isinstance(predictions, list) and len(predictions) == 2 and all(
            isinstance(item, dict)
            and isinstance(item.get("label"), str)
            and isinstance(item.get("score"), (int, float))
            and math.isfinite(item.get("score"))
            and 0 <= item.get("score") <= 1
            for item in predictions
        )
        return ok, f"predictions={len(predictions) if isinstance(predictions, list) else 'invalid'}"
    return False, f"Unknown response check: {check}"


def test_pack(pack_name: str, cfg: dict[str, Any], dist_dir: Path,
              base_override: str | None, timeout: float) -> dict[str, Any]:
    base_url = base_override or f"http://127.0.0.1:{cfg['port']}"
    env = read_env(dist_dir / pack_name / ".env")
    admin_token = os.environ.get(cfg["admin_env"]) or env.get(cfg["admin_env"], "")
    results: list[dict[str, Any]] = []
    license_key = None
    key_hash = None

    try:
        status, health, elapsed = request_json(base_url, "/health", timeout=min(timeout, 15))
        health_ok = status == 200 and isinstance(health, dict) and health.get("status") == "healthy"
        add_result(results, "gateway and all configured service health checks", health_ok,
                   status, elapsed, json.dumps(health, ensure_ascii=False)[:600])
    except Exception as exc:
        add_result(results, "gateway and all configured service health checks", False,
                   None, None, f"{type(exc).__name__}: {exc}")
        return {"pack": pack_name, "base_url": base_url, "tests": results}

    if len(admin_token) < 32 or admin_token == "CHANGE_ME":
        add_result(results, "create temporary test license", False, None, None,
                   f"Set {cfg['admin_env']} in {dist_dir / pack_name / '.env'} to a random secret (>=32 chars)")
        return {"pack": pack_name, "base_url": base_url, "tests": results}

    try:
        status, created, elapsed = request_json(
            base_url, "/admin/license/create", method="POST",
            payload={"domain": "smoke-test.local", "plan": "enterprise", "expires": "2099-12-31"},
            headers={"X-Admin-Token": admin_token}, timeout=timeout,
        )
        if status != 200 or not isinstance(created, dict) or not created.get("license_key") or not created.get("key_hash"):
            add_result(results, "create temporary test license", False, status, elapsed,
                       json.dumps(created, ensure_ascii=False)[:400])
            return {"pack": pack_name, "base_url": base_url, "tests": results}
        license_key, key_hash = created["license_key"], created["key_hash"]
        add_result(results, "create temporary test license", True, status, elapsed, "temporary key created; key value hidden")

        status, valid, elapsed = request_json(
            base_url, "/license/validate", headers={"X-License-Key": license_key}, timeout=timeout,
        )
        ok = status == 200 and isinstance(valid, dict) and valid.get("status") == "active"
        add_result(results, "license validation", ok, status, elapsed,
                   f"status={valid.get('status')!r}, plan={valid.get('plan')!r}" if isinstance(valid, dict) else str(valid)[:300])

        for spec in cfg["tests"]:
            try:
                status, response, elapsed = request_json(
                    base_url, spec["path"], method=spec["method"], payload=spec.get("payload"),
                    headers={"X-License-Key": license_key}, timeout=timeout,
                )
                if status < 200 or status >= 300:
                    ok, detail = False, json.dumps(response, ensure_ascii=False)[:400]
                else:
                    ok, detail = validate_payload(spec["check"], response)
                add_result(results, spec["name"], ok, status, elapsed, detail)
            except Exception as exc:
                add_result(results, spec["name"], False, None, None,
                           f"{type(exc).__name__}: {exc}")

        status, usage, elapsed = request_json(
            base_url, "/usage", headers={"X-License-Key": license_key}, timeout=timeout,
        )
        ok = status == 200 and isinstance(usage, dict) and usage.get("usage_unit") == "credits"
        add_result(results, "usage endpoint and quota snapshot", ok, status, elapsed,
                   f"usage_unit={usage.get('usage_unit')!r}" if isinstance(usage, dict) else str(usage)[:300])

    except Exception as exc:
        add_result(results, "gateway smoke test", False, None, None, f"{type(exc).__name__}: {exc}")
    finally:
        if license_key and key_hash and len(admin_token) >= 32:
            try:
                status, revoked, elapsed = request_json(
                    base_url, f"/admin/license/{key_hash}", method="DELETE",
                    headers={"X-Admin-Token": admin_token}, timeout=timeout,
                )
                add_result(results, "revoke temporary test license", status in (200, 204),
                           status, elapsed, "temporary key revoked" if status in (200, 204) else str(revoked)[:250])
            except Exception as exc:
                add_result(results, "revoke temporary test license", False, None, None,
                           f"{type(exc).__name__}: {exc}")

    return {"pack": pack_name, "base_url": base_url, "tests": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, default=Path(__file__).resolve().parents[1] / "dist")
    parser.add_argument("--pack", choices=["all", *PACKS], default="all")
    parser.add_argument("--base-url", help="Override gateway URL (only with --pack for one pack)")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--json-output", type=Path, help="Write report JSON to this path")
    args = parser.parse_args()
    if args.base_url and args.pack == "all":
        parser.error("--base-url can be used only with a single --pack")
    selected = list(PACKS) if args.pack == "all" else [args.pack]
    report: dict[str, Any] = {
        "report_type": "live_smoke_test_not_model_benchmark",
        "runtime_checks": [],
        "capability_gaps": [],
        "release_note": "A passing smoke test is not proof of model accuracy, legal clearance, trained production models, payment/billing readiness, or public-sale readiness.",
    }
    for pack_name in selected:
        cfg = PACKS[pack_name]
        item = test_pack(pack_name, cfg, args.dist_dir, args.base_url, args.timeout)
        report["runtime_checks"].append(item)
        report["capability_gaps"].extend(
            {"pack": pack_name, "gap": gap} for gap in cfg["capability_gaps"]
        )

    failures = [
        (item["pack"], result["test"])
        for item in report["runtime_checks"] for result in item["tests"]
        if result["status"] != "PASS"
    ]
    report["runtime_status"] = "PASS" if not failures else "FAIL"
    report["release_status"] = "NOT_READY_FOR_PUBLIC_SALE" if failures or report["capability_gaps"] else "REVIEW_REQUIRED"
    serialized = json.dumps(report, ensure_ascii=False, indent=2)
    print(serialized)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(serialized + "\n", encoding="utf-8")
    return 1 if failures else (2 if report["capability_gaps"] else 0)


if __name__ == "__main__":
    raise SystemExit(main())
