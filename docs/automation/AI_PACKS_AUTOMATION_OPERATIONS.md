# AI Packs GitHub Automation Operations Runbook

**Status:** DRAFT — NOT READY  
**Scope:** `yarsalam/ai-packs` GitHub automation only  
**Last reviewed:** 2026-11-10

This runbook is an operator procedure, not authorization to merge, auto-merge, publish, release, deploy, change production, access secret values, spend money, or resume product work. Issue [#28](https://github.com/yarsalam/ai-packs/issues/28) remains the controlling acceptance gate.

## 1. Non-negotiable safety boundary

- Keep product PRs #26 and #27 open and Draft. Keep policy PR #29 Draft until reviewed. Keep infrastructure PRs Draft until separately reviewed.
- Never merge or enable auto-merge. Never merge `yarsalam/mobApp` PR #6 without separate explicit owner authorization.
- Do not dispatch manual-only or self-hosted workflows. Do not assume the owner's laptop or local runner is online.
- Do not publish GHCR images, create releases, deploy, change production, or run product/data/research/benchmark work.
- Do not enable scoring, ranking, probability calibration, backtesting, broker/trading, or capital allocation.
- Never read or emit secret values, tokens, environment values, raw logs, exception payloads, private paths, customer data, datasets, or model files.
- Use GitHub-hosted standard `ubuntu-latest` runners for cloud CI. Do not select larger runners or add paid services/agents.

## 2. Repository and cost boundary

The repository was verified as **public** on 2026-11-10. The seven workflows currently on `main` use GitHub-hosted `ubuntu-latest` runners. GitHub documents standard GitHub-hosted runner use as free for public repositories; larger runners can still be billed even for public repositories. See [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

Artifact and cache storage are separate from standard-runner compute. Their allowance and any account-level overage/spending cap are not established by this runbook. Keep artifact retention short, upload only necessary small validation outputs, and do not enable recurring or agent workloads until the owner has verified that paid overage is disabled or capped at zero. The total account storage and billing settings remain an owner-only verification item.

Because this repository is public, GitHub documents protected branches as available on GitHub Free; a paid-plan upgrade is not required just to protect `main`. See [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches). However, no AI Packs repository ruleset was visible in the latest audit, and the owner's latest CLI observation (2026-11-09) reported `main` as not protected. Do not treat the branch as protected until an owner configures and verifies required checks, PR-only changes, and force-push/deletion restrictions.

## 3. Daily operator preflight

Before interpreting any green check:

1. Read the current default-branch SHA and commit timestamp.
2. Read the latest `push` run on `main`; confirm its `head_sha` exactly matches current `main`.
3. For every open PR, read its current head SHA and inspect checks/runs attached to that exact SHA. A green run on an older SHA does not validate the current head.
4. Inspect queued and in-progress runs repository-wide. If none exist, report zero; if the API scan is truncated, report the limitation rather than assuming no stale jobs.
5. Query schedule runs with both `event=schedule` and `branch=main`. A schedule job skipped on a pull-request event is not schedule evidence.
6. Confirm that the latest real scheduled run on the default branch completed successfully. Do not call a schedule operational before that evidence exists.
7. Keep all unknown settings explicitly marked Unknown.

For this repository, the current seven main-branch workflows have no scheduled health workflow. The proposed `automation-health.yml` exists only in the Draft infrastructure PR stack. Its schedule is inactive until an owner-authorized change places it on the default branch. This runbook does not authorize merging that PR.

## 4. Run and check interpretation

- **success:** count only when the run's exact `head_sha` is the current commit being assessed.
- **skipped:** expected for jobs whose event condition does not match (for example, schedule-only jobs during `pull_request`). Never count a skipped scheduled job as a scheduled success.
- **cancelled:** compare the cancelled run's SHA/ref with the newest run. A cancelled older PR SHA may be superseded; it is not automatically a test failure.
- **failure / timed out:** classify before any rerun. Do not repeatedly rerun a deterministic failure.
- **queued / in progress:** inspect the job state and age. Do not poll every minute or start an unbounded loop.

The proposed health monitor uses these thresholds: queued job older than 30 minutes, running job older than 300 minutes, last successful main run older than 36 hours, and previous scheduled health run older than 36 hours. It inspects at most the oldest 10 active runs and must report truncation. These thresholds are detection rules, not an uptime SLA.

## 5. Retry policy

The proposed health monitor retries only idempotent GitHub API GET requests:

- Retry transient HTTP 500, 502, 503, 504 and network transport/time-out failures.
- Maximum three total attempts, with bounded 1-second and 2-second delays.
- Do not retry any 4xx response (including 408 or 429), permission/authentication failures, invalid JSON, invalid response shape, test failures, or invalid data.
- Never automatically rerun an entire workflow or an arbitrary failed job.
- A retry succeeding does not prove that the underlying service is continuously healthy.

## 6. Concurrency and queue limitations

- Stateless PR validation may cancel only an older run for the same PR/ref when a newer commit supersedes it.
- Different PRs/refs must have independent concurrency groups.
- Any future job that mutates shared state must use non-cancelling serialization and must never overlap destructively.
- GitHub Actions concurrency is not a durable FIFO queue: it allows one running and one pending run per group, and a newer pending run can replace the existing pending run.
- Therefore, do not claim a durable stateful queue from a concurrency-group setting alone. No current AI Packs workflow has an approved persistent stateful job. Issue #28's controlled concurrency/stateful-queue proof remains open.

## 7. Health notification and recovery

The proposed health workflow has a separate failure-only notifier. It is scoped to `issues: write` and is intended to post only a run link, event, attempt number, and short SHA to Issue #28. The notifier is skipped during normal pull-request validation. Unit/contract tests and a green PR run do not prove that a real notification was delivered.

Recovery procedure:

1. Open the exact failed run and confirm its SHA, event, workflow, and job.
2. Determine whether cancellation was caused by a newer run, an actual failure, or a timeout.
3. Inspect only the minimum failing step needed. Do not copy raw logs or exception output into an issue or chat.
4. Retry only a confirmed transient, idempotent operation within the bounded policy above.
5. For deterministic, permission, invalid-data, repeated, or unclear failures, stop and hand off to the owner with the run link and sanitized status.
6. Confirm a notification only if the sanitized Issue #28 comment is actually visible. If it is absent, delivery is unconfirmed; the Actions run remains the source of truth.
7. Do not automatically cancel, rerun, merge, publish, deploy, or modify production as part of recovery.

No end-to-end failure notification, controlled timeout/cancellation, or recovery test has been accepted yet.

## 8. Runner, secrets, and artifact boundaries

- Current AI Packs main workflows use GitHub-hosted `ubuntu-latest`.
- The latest owner-provided repository-level inventory (2026-11-09) reported zero self-hosted runners, zero repository Actions secrets, and zero environments. This does not enumerate organization-level runners/secrets; those remain Unknown.
- Never use a laptop runner as a persistent service. A self-hosted runner is out of scope unless a concrete cloud limitation is demonstrated and the owner approves a separate, isolated server design.
- Current main retains the distribution artifact for 14 days and the WordPress preview artifact for 30 days. The proposed CI-hardening PR reduces the WordPress preview retention to 14 days. Treat the proposed setting as inactive until merged by an authorized owner.
- Sampled recent PR artifacts were small (about 241 KB for a distribution archive and 28 KB for the WordPress preview); this is not a measurement of total account storage.
- Workflow logs have their own retention setting; the current account/repository log-retention configuration is Unknown.
- No secret values are needed for ordinary CI. Never add a broad PAT or unbounded API key.

## 9. Agent and durable queue decision

A bounded issue-to-PR agent has not been enabled or proven. With a zero additional budget, do not add a paid Copilot cloud-agent plan, external model API, paid queue, or broad credential. The agent acceptance item remains blocked/unavailable unless a no-cost, least-privilege capability is explicitly verified and separately authorized.

If future work requires a durable stateful queue, first document why GitHub concurrency is insufficient and design a no-cost, least-privilege persistence mechanism. Do not silently substitute a one-pending-run concurrency group for a durable queue.

## 10. Readiness gate

Keep the overall status **NOT READY** until Issue #28 has linked evidence for all of the following:

- push/PR checks and a real successful schedule on default branch;
- controlled same-PR supersession, independent PR isolation, and stateful queue non-overlap;
- controlled timeout and cancellation;
- bounded transient retry and permanent no-retry;
- deliberate failure with sanitized notification actually delivered;
- stale queued/running and missing-heartbeat detection plus recovery;
- explicit least-privilege permissions and timeouts on every job;
- owner-verified branch protection, required checks, no force-push/delete;
- owner-verified Actions usage, storage and zero-overage/spending boundary;
- runner inventory and independent health/recovery if any server runner is required;
- operator runbook and a bounded issue-to-PR agent test, if a no-cost authorized agent is available;
- no prohibited merge, release, publish, deployment, secret access, product work, or financial action.

Until every item is evidenced, keep ordinary product development and release preparation paused.
