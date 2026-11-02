# Persian Safety benchmark protocol

## Dataset format

Use UTF-8 JSON Lines. One manually labelled record per line:

```json
{"text":"سلام، حالت خوبه؟","expected_action":"allow","expected_category":"clean"}
{"text":"بیا در تلگرام صحبت کنیم","expected_action":"review","expected_category":"external_contact"}
{"text":"عبارت نمونه‌ای که طبق سیاست مشتری باید مسدود شود","expected_action":"block","expected_category":"custom_policy"}
```

Allowed actions: `allow`, `review`, `block`. Category labels should be agreed by the annotation guideline before labelling starts.

## Data governance

- Use only data with a documented legal basis/consent for evaluation; remove names, phone numbers, IDs and other direct identifiers before sharing a dataset.
- Prefer synthetic examples for routine CI. Keep real evaluation corpora private and access-controlled; never commit private user messages to this public repository.
- Separate training/tuning data from validation and sealed test data by source or time. Do not tune thresholds on the sealed test set.
- Double-annotate a sample and resolve disagreements. Document language variety (formal Persian, colloquial Persian, Finglish, typo, code-switching), content context and category definition.
- Do not present synthetic CI fixtures as a real-world quality benchmark.

## Run an evaluation

Create an API key in a private test environment, then:

```bash
export SAFETY_PACK_URL="https://your-test-gateway.example"
export SAFETY_PACK_LICENSE_KEY="(keep it in your shell secret store)"
python scripts/evaluate_moderation.py \
  --dataset /secure/path/persian-safety-test.jsonl \
  --output /secure/path/evaluation-report.json
```

The runner refuses plain HTTP to remote hosts, keeps the key out of command-line arguments, and writes aggregate metrics only. It does not include submitted text in the report. Keep the dataset itself protected.

## Metrics

- Three-class action accuracy and macro-F1.
- Precision, recall and F1 for allow/review/block.
- Binary flagged-vs-allow false-positive and false-negative counts/rates.
- Confusion matrix and per-category precision/recall/F1.
- p50, p95 and mean end-to-end latency.

Do not call the model score a calibrated probability. Report support/sample counts with every metric. The first release gate is at least 1,000 reviewed examples as a starting point, followed by larger and refreshed sets based on the customer's risk and traffic profile; the sample threshold is not a guarantee of statistical sufficiency for every use case.
