#!/usr/bin/env python3
"""Evaluate a Safety Pack moderation endpoint against a consented JSONL benchmark.

Input records: {"text": "...", "expected_action": "allow|review|block",
                "expected_category": "optional-category"}
Raw text is never written to the report. Keep benchmark files access-controlled.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ACTIONS = ("allow", "review", "block")


def validate_base_url(value: str):
    parsed = urlsplit(value)
    if parsed.username or parsed.password or not parsed.hostname:
        raise ValueError("base URL must contain a hostname and no embedded credentials")
    if parsed.scheme == "https":
        return parsed
    if parsed.scheme == "http" and parsed.hostname.lower() in {"localhost", "127.0.0.1", "::1"}:
        return parsed
    raise ValueError("Use HTTPS, or plain HTTP only for localhost/loopback")


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(req.full_url, code, "redirects are disabled for authenticated evaluation", headers, fp)


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil((pct / 100) * len(ordered)) - 1))
    return round(ordered[index], 2)


def class_metrics(expected: list[str], predicted: list[str], label: str) -> dict[str, Any]:
    tp = sum(e == label and p == label for e, p in zip(expected, predicted))
    fp = sum(e != label and p == label for e, p in zip(expected, predicted))
    fn = sum(e == label and p != label for e, p in zip(expected, predicted))
    support = sum(e == label for e in expected)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "support": support,
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }


def build_report(records: list[dict[str, Any]], latencies_ms: list[float], errors: int = 0) -> dict[str, Any]:
    expected = [str(row["expected_action"]) for row in records]
    predicted = [str(row["predicted_action"]) for row in records]
    confusion = {
        actual: {guess: sum(e == actual and p == guess for e, p in zip(expected, predicted)) for guess in ACTIONS}
        for actual in ACTIONS
    }
    per_action = {label: class_metrics(expected, predicted, label) for label in ACTIONS}
    flagged_expected = ["flagged" if item != "allow" else "allow" for item in expected]
    flagged_predicted = ["flagged" if item != "allow" else "allow" for item in predicted]
    binary = class_metrics(flagged_expected, flagged_predicted, "flagged")

    category_labels = sorted({
        str(row["expected_category"]) for row in records if row.get("expected_category")
    })
    category_metrics: dict[str, Any] = {}
    for category in category_labels:
        actual = [str(row.get("expected_category") or "") for row in records]
        guess = [str(row.get("predicted_category") or "") for row in records]
        category_metrics[category] = class_metrics(actual, guess, category)

    total = len(records)
    exact = sum(e == p for e, p in zip(expected, predicted))
    macro_f1 = sum(per_action[action]["f1"] for action in ACTIONS) / len(ACTIONS)
    return {
        "schema_version": 1,
        "evaluation": "safety-pack-moderation",
        "samples": total,
        "request_errors": errors,
        "action_accuracy": round(exact / total, 4) if total else None,
        "macro_f1_actions": round(macro_f1, 4) if total else None,
        "per_action": per_action,
        "flagged_vs_allow": {
            **binary,
            "false_positive_rate": round(
                binary["fp"] / sum(item == "allow" for item in flagged_expected), 4
            ) if sum(item == "allow" for item in flagged_expected) else None,
            "false_negative_rate": round(
                binary["fn"] / sum(item == "flagged" for item in flagged_expected), 4
            ) if sum(item == "flagged" for item in flagged_expected) else None,
        },
        "confusion_matrix": confusion,
        "per_category": category_metrics,
        "latency_ms": {
            "p50": percentile(latencies_ms, 50),
            "p95": percentile(latencies_ms, 95),
            "mean": round(statistics.fmean(latencies_ms), 2) if latencies_ms else None,
        },
        "privacy": "raw input text is intentionally omitted from this report",
    }


def load_dataset(path: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at line {line_number}") from exc
            if not isinstance(row, dict) or not isinstance(row.get("text"), str):
                raise ValueError(f"line {line_number} must contain a string text field")
            action = row.get("expected_action")
            if action not in ACTIONS:
                raise ValueError(f"line {line_number} expected_action must be allow, review, or block")
            category = row.get("expected_category", "")
            if category and not isinstance(category, str):
                raise ValueError(f"line {line_number} expected_category must be a string")
            records.append({
                "text": row["text"],
                "expected_action": action,
                "expected_category": category,
            })
    if not records:
        raise ValueError("benchmark dataset is empty")
    return records


def call_endpoint(base_url: str, license_key: str, text: str) -> tuple[dict[str, Any], float]:
    payload = json.dumps({"text": text, "context": "message"}, ensure_ascii=False).encode("utf-8")
    request = Request(
        base_url.rstrip("/") + "/moderate/decision",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-License-Key": license_key,
        },
        method="POST",
    )
    started = time.perf_counter()
    try:
        opener = build_opener(NoRedirectHandler)
        with opener.open(request, timeout=35) as response:
            body = json.loads(response.read(1024 * 1024).decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"API returned HTTP {exc.code}") from None
    except URLError as exc:
        raise RuntimeError(f"API request failed: {type(exc.reason).__name__}") from None
    elapsed = (time.perf_counter() - started) * 1000
    if not isinstance(body, dict) or body.get("action") not in ACTIONS:
        raise RuntimeError("API response did not contain a valid action")
    return body, elapsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--base-url", default=os.getenv("SAFETY_PACK_URL", "http://127.0.0.1:9001"))
    parser.add_argument("--output", type=Path, help="Optional aggregate JSON report path")
    args = parser.parse_args()

    license_key = os.getenv("SAFETY_PACK_LICENSE_KEY", "")
    if not license_key:
        parser.error("Set SAFETY_PACK_LICENSE_KEY in the environment; do not pass it on the command line.")
    try:
        validate_base_url(args.base_url)
    except ValueError as exc:
        parser.error(str(exc))

    try:
        dataset = load_dataset(args.dataset)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    results: list[dict[str, Any]] = []
    latencies: list[float] = []
    errors = 0
    for index, row in enumerate(dataset, start=1):
        try:
            output, elapsed = call_endpoint(args.base_url, license_key, row["text"])
            results.append({
                "expected_action": row["expected_action"],
                "predicted_action": output["action"],
                "expected_category": row["expected_category"],
                "predicted_category": output.get("category", ""),
            })
            latencies.append(elapsed)
        except RuntimeError as exc:
            errors += 1
            print(f"sample {index}: {exc}", file=sys.stderr)

    report = build_report(results, latencies, errors)
    report["dataset_path"] = args.dataset.name
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
