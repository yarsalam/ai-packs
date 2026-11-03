# Public release gates — AI Packs

**Current decision: NO-GO (2026-11-03).** This is a release-control record, not a claim that the products have passed the listed gates.

## Why public publishing is disabled

The repository currently contains a technical preview. A green CI run proves that the tested code paths build and pass their automated tests; it does not prove production inference quality, commercial model rights, privacy compliance, operating cost, or readiness for customer traffic.

Until every gate below has evidence and the Safety pilot issue [#8](https://github.com/yarsalam/ai-packs/issues/8) records an explicit GO decision:

- GHCR publishing is disabled in all AI Pack image workflows.
- GitHub Release attachment/publication is disabled in the distribution workflow.
- Manual workflow dispatch may build and validate only; it cannot publish.
- Pull-request workflows build locally and upload only temporary GitHub Actions artifacts where configured.
- No VPS deployment is authorized by this document.

## Gate register

| Gate | Required evidence | Current state |
|---|---|---|
| Model and dependency licensing | Exact immutable model/weight revisions, checksums, package licenses, redistribution/hosting rights, dataset rights, legal review | **OPEN** |
| Persian inference quality | Lawfully sourced and de-identified Persian corpus; agreed labels; formal/colloquial/Finglish/typo/code-switch coverage; independent annotation and adjudication; train/tune/validation/sealed-test separation; reproducible metrics with support counts | **BLOCKED — no approved corpus** |
| Sealed evaluation | Sealed test access controls, immutable dataset/model/pack revisions, untouched test run, aggregate report | **NOT RUN** |
| Security | Threat model, auth/tenant isolation, abuse/rate limits, dependency/image scan, SBOM, secret handling, security review | **OPEN** |
| Privacy and retention | Data-flow map, lawful basis, DPA/consent where required, PII review, downstream log/cache/model retention and deletion verification | **OPEN** |
| Cold install and full inference | Clean isolated install from generated ZIPs, empty model cache, every service and model actually invoked, failure/recovery tests | **NOT COMPLETE** |
| Load, latency and cost | Agreed workload, throughput, error rate, p50/p95, resource profile, measured cost per 1,000 operations | **NOT MEASURED** |
| Human operations | Review queue, assignment, audit trail, appeal/reversal, escalation and incident/rollback runbooks | **PREVIEW ONLY** |
| Release authorization | All preceding gates evidenced; owner-reviewed go/no-go recorded in issue #8; a separate release change reviewed | **NOT AUTHORIZED** |

## Dataset candidate review (2026-11-03)

No candidate has been accepted as the commercial pilot corpus.

- [NASEZA](https://github.com/amirivojdan/naseza) declares CC0-1.0 and contains 5,719 Persian samples collected from Telegram political/sports discussions, with only Normal/Offensive labels. CC0 is useful copyright/database-rights metadata, but the CC0 text itself disclaims responsibility for clearing third-party rights and obtaining necessary consents. The public record does not establish a sufficient privacy/data-protection basis for this product's commercial pilot. Treat it as a candidate for legal review only; do not ingest it into the sealed benchmark yet.
- [PHate](https://github.com/Zahra-D/Phate) documents approximately 7,000 Persian hate-speech examples and train/validation/test files, but the repository metadata and file listing do not identify an explicit dataset license. Public availability is not commercial-use permission.
- [ParsHate](https://github.com/zbokaee/ParsHate) describes a 10,000-example public Persian hate/target benchmark, but its repository currently has only a README and no explicit repository license metadata. Public availability is not commercial-use permission.

These resources also do not, by themselves, cover the complete product taxonomy (commercial spam, off-platform contact, harassment/abuse, threats and clean content) or the intended dating/social-platform distribution. Do not merge them into a benchmark until the rights holder's permissions, provenance, privacy basis, permitted purpose, retention and redistribution terms have been documented and reviewed.

## Data governance implementation

The private dataset intake path and annotation protocol are documented in `docs/PERSIAN_SAFETY_DATA_COLLECTION_FA.md` and `docs/PERSIAN_SAFETY_ANNOTATION_GUIDE_FA.md`. The private manifest template and aggregate-only validator are `docs/templates/safety-benchmark-manifest.example.yaml` and `scripts/validate_safety_benchmark.py`. The template intentionally remains `pending`; the validator cannot turn an unlicensed dataset into an approved one. No raw corpus or consent evidence belongs in this public repository.

## Evidence already available

- Main commit `e04263027c00e64c6bed0b34488a670530557977` has a successful GitHub Actions run `41597682093` (Gateway contract matrix and Matching runtime image build/import check).
- PR #10 (`security/disable-public-publish-until-release-go-20261103`) merged with merge commit `63200213961e176f58fd643f40a38219d4d08b45`; all 8 checks passed on head `157faa5fd1ed3967c787e4fd8305f4afc3461720`.
- PR #11 (`feat/safety-benchmark-governance-tooling-20261103`) merged with merge commit `0d617dfa136e437f92e05087208b37785e5de44c`; all 8 checks passed on head `06b9ea5c8ca8e626cc8e88f5d9776febd819067f`, including 30 Safety governance/policy/evaluator tests and the generated-pack single/batch semantic-outage check.
- PR #12 (`fix/safety-benchmark-report-no-overwrite-20261103`) merged with merge commit `66239f69b05909a176f071001f967ead46936d93`; all 8 checks passed on head `2a6fd5a09f3439bcbf12f5a140055dc00bdf66bd`, including 31 Safety tests. Existing report targets are now rejected rather than overwritten.
- Post-merge main workflow run `41663587208` completed with all 5 checks successful. These results prove code/build paths only; they do not change the NO-GO release decision.
- PR #7 merged on 2026-11-03. Its CI included the Safety policy/evaluation tests, WordPress preview package, distribution build, and a generated Safety moderation-engine single/batch embedding-outage test.
- Those tests are bounded code/build evidence only. No real Persian benchmark metrics, complete cold inference, load profile or cost measurement have been produced.

## Required release decision

A future GO must reference:

1. The exact approved dataset manifest and private dataset version; no raw text in this public repository.
2. The annotation guideline version, annotator agreement/adjudication summary and split/source-group manifest.
3. The exact model, dependency, pack and upstream service revisions.
4. The untouched sealed-test aggregate report.
5. Security, privacy/retention, cold-install, load/latency/cost evidence.
6. A bounded pilot plan with agreed false-positive/false-negative, latency, cost and escalation thresholds.

Until then, keep issue #8 open and issue #9 (customer outreach) blocked. Do not publish GHCR images, create a public product release, make accuracy/ROI claims, or deploy to YarSalam production.
