#!/usr/bin/env python3
"""Validate a private Persian Safety benchmark manifest; emit aggregate counts only."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

ACTIONS = {"allow", "review", "block"}
CATEGORIES = {
    "clean", "commercial_spam", "external_contact", "harassment_abuse",
    "threat", "hate_speech", "sexual_safety", "other_policy_violation", "ambiguous",
}
VARIETIES = {"formal", "colloquial", "finglish", "typo", "code_switching", "other"}
CONTEXTS = {"message", "bio", "comment", "profile"}
SPLITS = {"train", "tune", "validation", "sealed_test"}
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
PII_PATTERNS = {
    "email": re.compile(r"(?i)(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?!\w)"),
    "phone": re.compile(r"(?<!\d)(?:(?:\+|00)?98|0)?9\d{9}(?!\d)"),
    "handle": re.compile(r"(?<!\w)@[A-Za-z0-9_]{3,}"),
    "url": re.compile(r"(?i)(?:https?://|www\.|t\.me/|telegram\.me/)[^\s]+"),
}


class ValidationError(ValueError):
    """Safe validation error; never includes submitted source text."""


def fail(message):
    raise ValidationError(message)


def mapping(value, label):
    if not isinstance(value, dict):
        fail(label + " must be a mapping")
    return value


def required(obj, key, label):
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(label + "." + key + " is required")
    return value.strip()


def positive_integer(value, label, minimum=1):
    # bool is a subclass of int in Python; reject it for numeric policy fields.
    if type(value) is not int or value < minimum:
        fail(label + " must be an integer >= " + str(minimum))
    return value


def pii_flags(value):
    value = unicodedata.normalize("NFKC", value).translate(DIGITS).replace("ك", "ک").replace("ي", "ی")
    return [name for name, pattern in PII_PATTERNS.items() if pattern.search(value)]


def opaque(obj, key, label):
    value = required(obj, key, label)
    if pii_flags(value):
        fail(label + "." + key + " must be an opaque identifier, not personal data")
    return value


def outside(path, root, label):
    path = path.resolve()
    if path.is_relative_to(root.resolve()):
        fail(label + " must be outside the public repository checkout")
    return path


def validate_manifest(manifest_path, repo_root, report_path=None):
    root = Path(repo_root).resolve()
    manifest_path = outside(Path(manifest_path), root, "manifest")
    report_target = None
    if report_path is not None:
        report_target = outside(Path(report_path), root, "aggregate report")
        if report_target == manifest_path:
            fail("aggregate report must not overwrite the manifest")
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValidationError("could not read a valid YAML manifest") from exc

    dataset = mapping(mapping(manifest, "manifest").get("dataset"), "dataset")
    # This value is copied into the aggregate report, so it must be opaque too.
    dataset_id = opaque(dataset, "id", "dataset")
    required(dataset, "version", "dataset")
    required(dataset, "owner", "dataset")

    source = mapping(dataset.get("source"), "dataset.source")
    for key in ("description", "collection_method", "rights_holder", "permission_reference"):
        required(source, key, "dataset.source")

    rights = mapping(dataset.get("rights"), "dataset.rights")
    if rights.get("status") != "approved" or rights.get("commercial_use") != "approved":
        fail("dataset rights and commercial_use must both be approved")
    for key in ("legal_basis", "evidence_reference", "reviewed_by", "reviewed_at"):
        required(rights, key, "dataset.rights")
    try:
        date.fromisoformat(rights["reviewed_at"])
    except ValueError as exc:
        raise ValidationError("dataset.rights.reviewed_at must use YYYY-MM-DD") from exc

    privacy = mapping(dataset.get("privacy"), "dataset.privacy")
    if privacy.get("status") != "approved":
        fail("dataset.privacy.status must be approved")
    if privacy.get("deidentification") != "completed" or privacy.get("pii_review") != "completed":
        fail("dataset de-identification and human PII review must be completed")
    positive_integer(privacy.get("retention_days"), "dataset.privacy.retention_days")
    required(privacy, "access_control", "dataset.privacy")
    required(privacy, "deletion_procedure", "dataset.privacy")

    annotation = mapping(dataset.get("annotation"), "dataset.annotation")
    required(annotation, "guideline_version", "dataset.annotation")
    positive_integer(annotation.get("minimum_annotators"), "dataset.annotation.minimum_annotators", minimum=2)
    if annotation.get("adjudication") != "completed":
        fail("dataset.annotation.adjudication must be completed")
    fraction = annotation.get("double_annotation_fraction")
    if isinstance(fraction, bool) or not isinstance(fraction, (int, float)) or not 0 < fraction <= 1:
        fail("dataset.annotation.double_annotation_fraction must be in (0, 1]")
    opaque(annotation, "adjudicator_id", "dataset.annotation")

    required_categories = dataset.get("required_categories", [])
    required_varieties = dataset.get("required_language_varieties", [])
    if not isinstance(required_categories, list) or any(not isinstance(x, str) for x in required_categories) or not set(required_categories) <= CATEGORIES:
        fail("dataset.required_categories contains unsupported labels")
    if not isinstance(required_varieties, list) or any(not isinstance(x, str) for x in required_varieties) or not set(required_varieties) <= VARIETIES:
        fail("dataset.required_language_varieties contains unsupported labels")

    policy = mapping(dataset.get("split_policy"), "dataset.split_policy")
    if policy.get("method") != "source_group" or policy.get("tuning_excludes_sealed_test") is not True:
        fail("split policy must split by source_group and exclude sealed_test from tuning")
    if policy.get("sealed_test_access") != "restricted":
        fail("sealed_test_access must be restricted")

    min_total = dataset.get("minimum_total_samples", 1000)
    min_sealed = dataset.get("minimum_sealed_test_samples", 100)
    min_category = dataset.get("minimum_category_support", 25)
    min_variety = dataset.get("minimum_language_variety_support", 10)
    for name, value in (("minimum_total_samples", min_total), ("minimum_sealed_test_samples", min_sealed),
                        ("minimum_category_support", min_category), ("minimum_language_variety_support", min_variety)):
        positive_integer(value, name)

    splits = mapping(dataset.get("splits"), "dataset.splits")
    if set(splits) != SPLITS:
        fail("dataset.splits must contain train, tune, validation and sealed_test")

    ids, groups, text_hashes = set(), {}, set()
    category_counts, variety_counts = Counter(), Counter()
    split_counts, double_count, total = {}, 0, 0

    for split in ("train", "tune", "validation", "sealed_test"):
        config = mapping(splits[split], "dataset.splits." + split)
        sealed = split == "sealed_test"
        if config.get("sealed") is not sealed:
            fail("dataset.splits." + split + ".sealed must be " + str(sealed).lower())
        data_path = Path(required(config, "path", "dataset.splits." + split))
        if not data_path.is_absolute():
            data_path = manifest_path.parent / data_path
        data_path = outside(data_path, root, split + " dataset")
        if report_target is not None and report_target == data_path:
            fail("aggregate report must not overwrite a dataset split")
        if not data_path.is_file():
            fail("dataset split file does not exist: " + split)

        count = 0
        try:
            handle = data_path.open("r", encoding="utf-8")
        except OSError as exc:
            raise ValidationError("could not open dataset split: " + split) from exc
        with handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                label = split + " line " + str(line_number)
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValidationError(label + " is not valid JSON") from exc
                row = mapping(row, label)
                sample_id = opaque(row, "sample_id", label)
                source_group = opaque(row, "source_group", label)
                text_value = row.get("text")
                if not isinstance(text_value, str) or not text_value.strip() or len(text_value) > 2000:
                    fail(label + " text must be non-empty and at most 2,000 characters")
                context, action, category = row.get("context"), row.get("expected_action"), row.get("expected_category")
                if not isinstance(context, str) or context not in CONTEXTS:
                    fail(label + " context is unsupported")
                if not isinstance(action, str) or action not in ACTIONS:
                    fail(label + " expected_action is unsupported")
                if not isinstance(category, str) or category not in CATEGORIES:
                    fail(label + " expected_category is unsupported")
                varieties = row.get("language_varieties")
                if not isinstance(varieties, list) or not varieties or any(not isinstance(x, str) for x in varieties) or not set(varieties) <= VARIETIES:
                    fail(label + " language_varieties is invalid")
                annotations = row.get("annotations")
                if not isinstance(annotations, list) or not annotations:
                    fail(label + " needs at least one annotation")
                annotator_ids, labels = [], []
                for item in annotations:
                    item = mapping(item, label + ".annotations[]")
                    annotator_ids.append(opaque(item, "annotator_id", label + ".annotations[]"))
                    a, c = item.get("action"), item.get("category")
                    if not isinstance(a, str) or a not in ACTIONS or not isinstance(c, str) or c not in CATEGORIES:
                        fail(label + " has an unsupported annotation label")
                    labels.append((a, c))
                if len(set(annotator_ids)) != len(annotator_ids):
                    fail(label + " annotator IDs must be distinct")
                adjudication = mapping(row.get("adjudication"), label + ".adjudication")
                status = adjudication.get("status")
                if not isinstance(status, str) or status not in {"single_review", "agreement", "resolved"}:
                    fail(label + " adjudication.status is invalid")
                if len(labels) == 1:
                    if status != "single_review" or labels[0] != (action, category):
                        fail(label + " single annotation must be reviewed and match the final label")
                    opaque(adjudication, "reviewer_id", label + ".adjudication")
                else:
                    if status == "single_review":
                        fail(label + " double annotation cannot be marked single_review")
                    if len(set(labels)) > 1:
                        if status != "resolved":
                            fail(label + " annotation disagreement must be resolved")
                        opaque(adjudication, "reviewer_id", label + ".adjudication")
                    elif status != "agreement" or any(x != (action, category) for x in labels):
                        fail(label + " final label must match agreeing annotations")

                flags = pii_flags(text_value)
                if flags:
                    fail(label + " failed PII screening (" + ",".join(flags) + "); inspect privately")
                digest = hashlib.sha256(re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text_value).casefold()).strip().encode("utf-8")).hexdigest()
                if sample_id in ids:
                    fail("duplicate sample_id across splits")
                if source_group in groups and groups[source_group] != split:
                    fail("source_group leakage between splits")
                if digest in text_hashes:
                    fail("duplicate normalized text detected")
                ids.add(sample_id)
                groups[source_group] = split
                text_hashes.add(digest)
                category_counts[category] += 1
                for variety in set(varieties):
                    variety_counts[variety] += 1
                double_count += int(len(labels) >= 2)
                count += 1
        if count == 0:
            fail("dataset split is empty: " + split)
        split_counts[split] = count
        total += count

    if total < min_total or split_counts["sealed_test"] < min_sealed:
        fail("dataset does not meet minimum total or sealed-test sample count")
    double_fraction = double_count / total
    if double_fraction < fraction:
        fail("double-annotation coverage is below the manifest minimum")
    if any(category_counts[x] < min_category for x in required_categories):
        fail("required category support is below the manifest minimum")
    if any(variety_counts[x] < min_variety for x in required_varieties):
        fail("required language-variety support is below the manifest minimum")

    return {
        "schema_version": 1,
        "dataset_id": dataset_id,
        "total_samples": total,
        "split_counts": split_counts,
        "category_support": dict(sorted(category_counts.items())),
        "language_variety_support": dict(sorted(variety_counts.items())),
        "source_groups": len(groups),
        "double_annotated_samples": double_count,
        "double_annotation_fraction": round(double_fraction, 4),
        "pii_screen": "passed; heuristic only, not a substitute for human review",
        "raw_text_in_report": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report", type=Path, help="Optional aggregate-only JSON report outside the repository")
    args = parser.parse_args()
    try:
        result = validate_manifest(args.manifest, args.repo_root, args.report)
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.report:
            report_target = Path(args.report).resolve()
            report_target.parent.mkdir(parents=True, exist_ok=True)
            report_target.write_text(rendered, encoding="utf-8")
        sys.stdout.write(rendered)
        return 0
    except (ValidationError, OSError) as exc:
        print("benchmark validation failed: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
