import importlib.util
import json
from pathlib import Path

import pytest
import yaml

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "validate_safety_benchmark.py"
SPEC = importlib.util.spec_from_file_location("validate_safety_benchmark", MODULE)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
ValidationError = validator.ValidationError
validate_manifest = validator.validate_manifest


def record(i, category="clean", variety="formal", group=None, text=None, double=False):
    annotations = [{"annotator_id": "ann-a", "action": "allow", "category": category}]
    adjudication = {"status": "single_review", "reviewer_id": "adj-01"}
    if double:
        annotations.append({"annotator_id": "ann-b", "action": "allow", "category": category})
        adjudication = {"status": "agreement"}
    return {
        "sample_id": f"sample-{i}", "source_group": group or f"source-{i}",
        "text": text or f"synthetic unit-test fixture {i}", "context": "message",
        "language_varieties": [variety], "expected_action": "allow",
        "expected_category": category, "annotations": annotations, "adjudication": adjudication,
    }


def make_manifest(tmp_path, pii=False):
    # These synthetic strings are validator unit-test fixtures, never benchmark/user data.
    rows = {
        "train": [record(1, "clean", "formal", double=True), record(2, "external_contact", "colloquial", double=True), record(3), record(4, "external_contact")],
        "tune": [record(5)], "validation": [record(6)],
        "sealed_test": [record(7), record(8)],
    }
    if pii:
        rows["sealed_test"][0]["text"] = "synthetic PII screening fixture 09123456789"
    splits = {}
    for name, values in rows.items():
        path = tmp_path / f"{name}.jsonl"
        path.write_text("".join(json.dumps(x) + "\n" for x in values), encoding="utf-8")
        splits[name] = {"path": str(path), "sealed": name == "sealed_test"}
    dataset = {
        "id": "private-test-corpus", "version": "1.0.0", "owner": "test-owner",
        "source": {"description": "test source", "collection_method": "opt-in test panel", "rights_holder": "test-owner", "permission_reference": "private-consent:TEST"},
        "rights": {"status": "approved", "commercial_use": "approved", "legal_basis": "documented consent", "evidence_reference": "private-review:TEST", "reviewed_by": "reviewer-01", "reviewed_at": "2026-11-03"},
        "privacy": {"status": "approved", "deidentification": "completed", "pii_review": "completed", "retention_days": 90, "access_control": "restricted private storage", "deletion_procedure": "verified deletion ticket"},
        "annotation": {"guideline_version": "1.0", "minimum_annotators": 2, "double_annotation_fraction": 0.25, "adjudication": "completed", "adjudicator_id": "adj-01"},
        "split_policy": {"method": "source_group", "tuning_excludes_sealed_test": True, "sealed_test_access": "restricted"},
        "minimum_total_samples": 8, "minimum_sealed_test_samples": 2,
        "minimum_category_support": 1, "minimum_language_variety_support": 1,
        "required_categories": ["clean", "external_contact"], "required_language_varieties": ["formal", "colloquial"],
        "splits": splits,
    }
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump({"dataset": dataset}), encoding="utf-8")
    return path, rows


def test_valid_manifest_returns_aggregate_only_report(tmp_path):
    manifest, _ = make_manifest(tmp_path)
    report = validate_manifest(manifest, tmp_path / "public-repo")
    assert report["total_samples"] == 8
    assert report["split_counts"]["sealed_test"] == 2
    assert report["double_annotation_fraction"] == 0.25
    assert report["raw_text_in_report"] is False


def test_rejects_missing_commercial_rights(tmp_path):
    manifest, _ = make_manifest(tmp_path)
    obj = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    obj["dataset"]["rights"]["commercial_use"] = "pending"
    manifest.write_text(yaml.safe_dump(obj), encoding="utf-8")
    with pytest.raises(ValidationError, match="rights and commercial_use"):
        validate_manifest(manifest, tmp_path / "public-repo")


def test_rejects_personal_data_in_reported_dataset_id(tmp_path):
    manifest, _ = make_manifest(tmp_path)
    obj = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    obj["dataset"]["id"] = "09123456789"
    manifest.write_text(yaml.safe_dump(obj), encoding="utf-8")
    with pytest.raises(ValidationError, match="opaque identifier"):
        validate_manifest(manifest, tmp_path / "public-repo")


def test_rejects_boolean_retention_days(tmp_path):
    manifest, _ = make_manifest(tmp_path)
    obj = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    obj["dataset"]["privacy"]["retention_days"] = True
    manifest.write_text(yaml.safe_dump(obj), encoding="utf-8")
    with pytest.raises(ValidationError, match="retention_days must be an integer"):
        validate_manifest(manifest, tmp_path / "public-repo")


def test_rejects_boolean_sample_minimum(tmp_path):
    manifest, _ = make_manifest(tmp_path)
    obj = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    obj["dataset"]["minimum_total_samples"] = True
    manifest.write_text(yaml.safe_dump(obj), encoding="utf-8")
    with pytest.raises(ValidationError, match="minimum_total_samples must be an integer"):
        validate_manifest(manifest, tmp_path / "public-repo")


def test_report_cannot_overwrite_dataset_split(tmp_path):
    manifest, _ = make_manifest(tmp_path)
    with pytest.raises(ValidationError, match="must not overwrite a dataset split"):
        validate_manifest(manifest, tmp_path / "public-repo", tmp_path / "train.jsonl")


def test_report_cannot_overwrite_manifest(tmp_path):
    manifest, _ = make_manifest(tmp_path)
    with pytest.raises(ValidationError, match="must not overwrite the manifest"):
        validate_manifest(manifest, tmp_path / "public-repo", manifest)


def test_rejects_source_group_leakage(tmp_path):
    manifest, rows = make_manifest(tmp_path)
    rows["sealed_test"][0]["source_group"] = rows["train"][0]["source_group"]
    (tmp_path / "sealed_test.jsonl").write_text("".join(json.dumps(x) + "\n" for x in rows["sealed_test"]), encoding="utf-8")
    with pytest.raises(ValidationError, match="source_group leakage"):
        validate_manifest(manifest, tmp_path / "public-repo")


def test_rejects_pii_without_echoing_text(tmp_path):
    manifest, _ = make_manifest(tmp_path, pii=True)
    with pytest.raises(ValidationError) as error:
        validate_manifest(manifest, tmp_path / "public-repo")
    assert "PII screening" in str(error.value)
    assert "09123456789" not in str(error.value)


def test_rejects_manifest_inside_public_checkout(tmp_path):
    manifest, _ = make_manifest(tmp_path)
    repo = tmp_path / "public-repo"
    repo.mkdir()
    inside = repo / "manifest.yaml"
    inside.write_text(manifest.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ValidationError, match="outside the public repository"):
        validate_manifest(inside, repo)


def test_rejects_duplicate_text_across_splits(tmp_path):
    manifest, rows = make_manifest(tmp_path)
    rows["sealed_test"][0]["text"] = rows["train"][0]["text"]
    (tmp_path / "sealed_test.jsonl").write_text("".join(json.dumps(x) + "\n" for x in rows["sealed_test"]), encoding="utf-8")
    with pytest.raises(ValidationError, match="duplicate normalized text"):
        validate_manifest(manifest, tmp_path / "public-repo")


def test_rejects_unsealed_test_split(tmp_path):
    manifest, _ = make_manifest(tmp_path)
    obj = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    obj["dataset"]["splits"]["sealed_test"]["sealed"] = False
    manifest.write_text(yaml.safe_dump(obj), encoding="utf-8")
    with pytest.raises(ValidationError, match="sealed_test.sealed"):
        validate_manifest(manifest, tmp_path / "public-repo")
