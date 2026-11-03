# Persian Safety benchmark protocol

**Current state (2026-11-03): tooling is being prepared; no legally approved pilot corpus or real model-quality result exists.** Do not treat CI fixtures, public previews, or the public dataset candidates listed in `docs/PERSIAN_SAFETY_DATA_COLLECTION_FA.md` as a product benchmark.

## Private dataset record format

Use UTF-8 JSON Lines. The following is a **schema-only placeholder**, not real user data and not a usable benchmark row:

```json
{"sample_id":"opaque-sample-id","source_group":"opaque-source-group","text":"<redacted text>","context":"message","language_varieties":["colloquial"],"expected_action":"review","expected_category":"external_contact","annotations":[{"annotator_id":"ann-a","action":"review","category":"external_contact"},{"annotator_id":"ann-b","action":"review","category":"external_contact"}],"adjudication":{"status":"agreement"}}
```

Allowed actions: `allow`, `review`, `block`. Categories and annotation rules are defined in `docs/PERSIAN_SAFETY_ANNOTATION_GUIDE_FA.md`. A final action/category must be adjudicated. At least the manifest-declared fraction (initially 20%) must have two independent annotators.

## Manifest and validation

Copy `docs/templates/safety-benchmark-manifest.example.yaml` to a **private location outside this repository**. Replace every placeholder only after rights, privacy and annotation review. The template intentionally uses `pending` statuses and must fail validation until approved.

```bash
python scripts/validate_safety_benchmark.py \
  --manifest /secure/private/safety/manifest.yaml \
  --report /secure/private/safety/validation-summary.json
```

The validator checks:

- explicit commercial-use permission and evidence references;
- completed de-identification and human PII review, retention and deletion controls;
- all four non-empty splits (`train`, `tune`, `validation`, `sealed_test`), with sealed access restricted;
- source-group disjointness and duplicate text across splits;
- action/category schema, annotation/adjudication consistency and double-annotation coverage;
- declared category/language-variety support and initial sample floors;
- manifest and data paths outside the public repository checkout;
- common email, Iranian mobile, social-handle and contact-URL patterns without printing the matched text.

The PII scan is heuristic only; it cannot prove that a dataset is anonymous or legally usable. Human privacy/legal review remains mandatory. The validator emits aggregate counts only and never writes raw text to its report.

Initial intake floors are 1,000 records overall and 100 sealed-test records, with at least 25 samples per required category and 10 per required language variety unless the manifest sets higher floors. These are project guardrails, not a claim of statistical sufficiency; sample size must be reviewed against prevalence and customer risk.

## Data governance

- Use only an opt-in partner corpus, an opt-in contributor panel, or a third-party dataset with explicit documented rights for the intended purpose.
- Record provenance, rights holder, lawful basis/consent or license, commercial-use permission, review evidence, retention, deletion and access controls in the private manifest.
- Do not scrape private groups/DMs, use production YarSalam messages, copy user data from production, or place raw benchmark data in this public repository.
- De-identify names, phone numbers, emails, handles, URLs and direct identifiers before annotation; exclude records that cannot be safely de-identified.
- Split by source/account/conversation group, not by individual message, to prevent leakage. Keep sealed-test access restricted and do not tune thresholds on it.
- Keep manifests, consent/DPA evidence, raw text, annotation exports and identity mappings in encrypted private storage. Never put them in GitHub issues, PRs, CI logs or artifacts.

See `docs/PERSIAN_SAFETY_DATA_COLLECTION_FA.md` for the full acquisition, privacy and deletion workflow.

## Run an evaluation

Only after the dataset passes validation, the model/pack is frozen, and the sealed-test custodian authorizes the run:

```bash
export SAFETY_PACK_URL="https://your-isolated-test-gateway.example"
export SAFETY_PACK_LICENSE_KEY="(retrieve from a private secret store)"
python scripts/evaluate_moderation.py \
  --dataset /secure/private/safety/sealed_test.jsonl \
  --output /secure/private/safety/sealed-test-report.json
```

The runner refuses plain HTTP to remote hosts, keeps the key out of command-line arguments, disables redirects for authenticated evaluation, and writes aggregate metrics only. Keep the dataset itself protected. A successful request run does not establish legal permission or statistical representativeness.

## Metrics

- Three-class action accuracy and macro-F1.
- Precision, recall and F1 for allow/review/block.
- Binary flagged-vs-allow false-positive and false-negative counts/rates.
- Confusion matrix and per-category precision/recall/F1.
- p50, p95 and mean end-to-end latency.

Report support/sample counts with every metric, dataset/model/pack/upstream revisions, request errors and known limitations. Do not call the model score a calibrated probability. No accuracy, fraud-reduction or ROI claim is allowed before the sealed report and issue #8 GO decision.
