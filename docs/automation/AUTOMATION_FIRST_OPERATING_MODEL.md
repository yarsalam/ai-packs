# AI Packs GitHub Automation — Infrastructure-First Operating Model

**Status:** NOT READY  
**Priority:** P0  
**Owner decision:** infrastructure automation is the only active workstream until the acceptance evidence in this document and [Issue #28](https://github.com/yarsalam/ai-packs/issues/28) is complete.  
**Last audited:** 2026-11-05

This document governs how automation work is designed and executed. It does not authorize merge, auto-merge, release, publish, deployment, production changes, secrets access, spending beyond an approved budget, broker/trading, investment scoring/ranking, probability calibration, backtesting approval, or capital allocation.

## 1. Operating rule

Until the infrastructure acceptance gate is met:

- Pause ordinary product feature development, commercial benchmarking, data/research work, release preparation and routine progression of existing feature PRs.
- Continue only work directly needed to design, build, secure, test, document or prove the GitHub automation system.
- Keep feature PRs open and Draft where they are Draft. Do not merge them as a way to make progress.
- Changes go to a dedicated branch and PR. Do not push infrastructure changes directly to main.
- When owner action is required, stop at a safe boundary and report one precise, complete action. Do not assume a laptop, local terminal, local runner or user credentials are available.
- Every monitoring execution produces a short Persian report, including no-change runs, with exactly one state: «در حال پیشرفت»، «منتظر اقدام کاربر» or «متوقف/مسدود». When no owner action is needed, say «فعلاً کاری از طرف تو لازم نیست».

The controlling issue is [P0 infrastructure automation issue #28](https://github.com/yarsalam/ai-packs/issues/28).

## 2. Audit baseline (2026-11-05)

### 2.1 AI Packs repository

Audited default-branch SHA: `0fe44582c4b9a673482319d4f11fb13d66dd6747`.

Seven workflow files were visible on main:

| Workflow | Trigger observed | Runner / limits observed | Current role |
| --- | --- | --- | --- |
| `.github/workflows/ci.yml` | pull_request, push | GitHub-hosted ubuntu-latest; concurrency exists; only matching image job had an explicit 90-minute timeout | Gateway contracts, PHP contracts, smoke-test contracts, Matching assistant image build/import check |
| `.github/workflows/ai-pack-control-agent-validation.yml` | pull_request, selected branch push | ubuntu-latest; contents:read | Compile and unit-test existing control-agent helper |
| `.github/workflows/distributions.yml` | pull_request, workflow_dispatch | ubuntu-latest; concurrency; no schedule | Build and validate stand-alone distributions; upload ZIP artifact |
| `.github/workflows/publish-matching-ai-assistant.yml` | workflow_dispatch | ubuntu-latest; concurrency; 90-minute timeout; contents:read | Validation-only image build |
| `.github/workflows/publish-other-ai-packs.yml` | pull_request, workflow_dispatch | ubuntu-latest; concurrency; 240-minute timeout; contents:read | Validation-only builds for selected/all services |
| `.github/workflows/publish-safety-pack.yml` | pull_request, workflow_dispatch | ubuntu-latest; concurrency; 180-minute timeout; contents:read | Validation-only Safety image builds |
| `.github/workflows/wordpress-showcase.yml` | pull_request, workflow_dispatch | ubuntu-latest; concurrency; contents:read | Preview ZIP validation/package; 30-day artifact retention |

Findings:
- No scheduled workflow was present in the audited workflow directory.
- No repository-wide scheduled health heartbeat, stale-run detector, tested failure notifier or bounded recovery workflow was evidenced.
- Some workflows define concurrency; all workflows/jobs do not yet have a complete, consistent timeout policy.
- The primary CI workflow did not declare an explicit workflow-level permissions block at the audited SHA. Effective repository default token permissions were not observable through the available connection.
- Image workflows say and implement validation-only behavior; they do not publish images in the audited flows. Preserve this boundary.
- Build artifact upload is currently used for distributions and the WordPress preview. Retention, contents, and cleanup must be reviewed per artifact type; no raw private data, credentials, model weights or local files may be uploaded.

Recent exact-head evidence:
- PR #26: head `eef94c0188c7bebc2890dec78726c4e5e0545f50`; open, Draft, reported mergeable; four latest observed checks passed in run IDs `41978094349`, `41978094383`, `41978094393`, `41978094411`.
- PR #27: head `621b6ef9297b4ed0bc45936e201056660f90bf3b`; open, Draft, reported mergeable; four observed checks passed in run IDs `41904116402`, `41904116476`, `41904116638`, `41904116910`.
- These results validate those product PR heads only. They are not proof of scheduled operation, recovery, health monitoring, branch protection or 24/7 readiness.

### 2.2 MarketSage comparison repository

The private `yarsalam/marketsage` repository was used as a design reference, not as proof that AI Packs is ready.

- Audited main SHA: `07e641670ceab22496ef976a584934464570fd9a`; latest observed main CI run `42060626605` succeeded.
- Its cloud CI uses GitHub-hosted `ubuntu-latest` runners.
- Local TSETMC workflows are manual-only and target self-hosted labels. A successful manual run proves availability only at that invocation; it does not prove an always-on server runner. The user's laptop is never an availability assumption.
- MarketSage PR #50, head `6a631b075a56e036e729bfa65ff3b87ec267f659`, proposes per-job timeouts, scoped concurrency, a daily schedule, a sanitized failure notice and an operator runbook. At audit time, exact-head run `42064376189` had five jobs complete successfully and its production-images job was still running. It was an open PR; schedule activation depends on landing the workflow on the default branch.
- GitHub scheduled workflows are periodic checks, not a real-time 24/7 SLA. They may be delayed under Actions load.

## 3. Target architecture

### 3.1 Cloud-first event-driven CI

Use GitHub-hosted runners for all work that can run in GitHub's cloud:

- Pull request opened, synchronized, reopened and ready-for-review events run targeted tests and relevant build validation.
- Pushes to main run the complete safe validation set.
- Pushes to approved infrastructure branches may run targeted infrastructure checks.
- Do not run local/private-data workflows from ordinary pushes, pull requests or schedules.
- Set workflow-level `permissions: contents: read` by default. Grant additional permissions only to a narrowly scoped job and only for its concrete purpose.
- Keep `persist-credentials: false` on checkout steps when later Git operations do not need the token.
- Pin third-party actions to verified full commit SHAs, with a human-readable version comment. Use dependency updates through PRs.

### 3.2 Scheduled health and status ledger

Add a low-cost daily workflow on GitHub-hosted runners. It should:

- Run the safe full CI or a deliberately selected health subset.
- Record the last successful run time, latest scheduled run, workflow state and current main SHA.
- Identify queued or in-progress jobs beyond documented thresholds, missing expected scheduled runs, disabled workflows and failed recent jobs.
- Produce a compact sanitized status summary. Do not attach logs or source data.
- Use a schedule time away from the top of the hour and document that GitHub can delay or drop scheduled events.
- Use the scheduled run as a heartbeat, not as a claim that the system is continuously executing.

### 3.3 Concurrency and queue safety

- Use a distinct concurrency key for workflow + PR number (or ref) so a newer run supersedes only the older run for that same PR/ref.
- For idempotent CI on pull requests, cancellation of a superseded run is acceptable.
- For jobs sharing state, persistent resources or external test environments, use non-cancelling concurrency and serialize access.
- Never allow two jobs to mutate the same workspace, external resource, quota counter or environment concurrently.
- Document that GitHub concurrency groups allow only one running and one pending execution per group; do not treat this as a general-purpose durable queue.
- Separate unrelated PRs and independent workflow classes into different concurrency groups.

### 3.4 Bounded retries, timeouts and cancellation

- Put explicit `timeout-minutes` on every job. Choose short limits for unit/contract tests and measured, documented limits for image builds.
- Use retries only around idempotent transient operations (network timeout, 502/503/429 with respectful backoff). Cap at 2–3 attempts with finite backoff and an overall deadline.
- Do not retry deterministic test failures, invalid inputs, 4xx responses, auth/permission errors or missing required configuration.
- Do not wrap an entire workflow in an unbounded retry loop. Do not rerun every job automatically.
- Distinguish superseded cancellation from genuine failure. Only retry a cancelled/failed job after identifying that a retry is safe.

### 3.5 Failure reporting and recovery

A separate reporting job/workflow may use a narrowly scoped token to post to the operational issue:

- Report workflow name, failed job names, short commit SHA, event type and GitHub run URL.
- Include a concise classification such as transient, deterministic, timeout, cancellation or permission failure only when supported by the job result.
- Never upload or quote raw logs, environment variables, exception dumps, local paths, secrets, tokens, datasets or model files.
- Scope write permission to the reporting job only (for example, `issues: write`); do not grant repository contents write, actions write, pull-request write or deployment permissions to ordinary CI.
- If notification fails, preserve the Actions run as the source of truth and record that delivery was not confirmed.

Recovery procedure:
1. Inspect the newest run for the exact PR/ref/SHA.
2. Determine whether cancellation was caused by a newer run or by an actual failure.
3. Inspect the minimum failing step needed; redact sensitive output.
4. Retry only a known transient/idempotent failure, at most once automatically or within the documented attempt cap.
5. For persistent failures, open/update a bounded operational issue and stop for human review.
6. Never automatically merge, publish, deploy or alter production as part of recovery.

### 3.6 Health checks and stale-run detection

Use a scheduled monitor with read-only Actions access to inspect:
- last successful run and its age;
- expected scheduled run versus observed schedule execution;
- jobs stuck queued or in progress longer than documented thresholds;
- workflow disabled/cancelled/failed status;
- repeated failures or exhausted retry limits.

The monitor should emit one deduplicated sanitized summary per run. Avoid minute-level polling. A missing heartbeat is an alertable condition, not proof that all workflows are broken.

### 3.7 Artifact, cache and log hygiene

- Prefer GitHub-hosted ephemeral workspaces and Actions cache for reproducible dependencies/build layers.
- Define retention days per artifact type and default to the shortest useful period.
- Upload only required test summaries or distribution outputs. Exclude raw datasets, customer information, model weights, `.env`, credentials, tokens, local paths, Docker socket data and unfiltered logs.
- Keep artifact names tied to a short SHA and run ID.
- Never use artifacts as an unreviewed code execution channel between privileged workflows.
- Cache is performance state, not an authority or a trusted source of truth; key by lockfile/platform/toolchain and avoid sharing writeable caches across untrusted contexts.

### 3.8 Runner policy

**Default:** GitHub-hosted runners for CI, tests, validation builds and scheduled health checks. The user's laptop runner must never be treated as always-on.

Only evaluate a self-hosted runner if a concrete task cannot reasonably run on GitHub-hosted compute. Any approved server runner must have:
- a dedicated machine independent of the user's laptop and production workload;
- a dedicated unprivileged OS account and restricted runner group scoped to this repository;
- no execution of fork or untrusted pull-request code;
- ephemeral/one-job isolation where available, clean workspace and disposable job state;
- restricted network egress, no unnecessary inbound ports and no broad cloud credentials;
- no root or Docker socket access for untrusted workloads;
- automatic security patching, runner-version updates and disk/memory/process health checks;
- system service supervision/restart, heartbeat/last-seen, alerts for offline/stuck jobs and a tested recovery runbook;
- limited concurrency and explicit job timeout.

A manual self-hosted workflow is not proof of persistent runner availability. Runner registration, labels, status and health must be verified independently before the runner can be called ready.

### 3.9 Human and secret boundary

- Do not read, echo, export or copy secret values into reports, artifacts or logs.
- Ordinary CI should not need repository secrets. For any future secret-dependent validation, use a dedicated environment, a human-approved test credential, narrowly scoped job permissions, masked output and no fork PR trigger.
- Secret metadata, branch protection, rulesets, Actions billing/budget, runner inventory and organization settings must be explicitly marked unknown until verified through authorized GitHub settings access.
- Any owner-only setting change must be prepared as a concise change proposal with expected impact, rollback and exact scope; do not change it speculatively.

### 3.10 Bounded coding-agent loop

A code-authoring agent may be evaluated only after:
1. main branch protection and required checks have been verified;
2. workflow token permissions and spending limits are known;
3. the agent can work from a bounded issue on a feature branch and open a PR;
4. the agent cannot merge, release, publish, deploy, access secrets or alter settings;
5. a test proves the agent's PR cannot bypass review/check gates.

If the required cloud agent is unavailable, document the limitation and evaluate a narrowly scoped alternative. Do not add a broad personal access token or uncapped API key. This is not permission to resume product work.

## 4. Implementation phases

| Phase | Work | Exit evidence |
| --- | --- | --- |
| A — Inventory | Workflow trigger/permissions/timeouts/concurrency/artifacts, runner labels, rules, secrets/billing visibility | Verified/unknown inventory; no assumptions |
| B — CI hardening | Explicit least privilege, per-job timeouts, safe concurrency, cache keys, bounded matrix/parallelism, artifact retention | Exact-head PR CI green; permission and timeout audit |
| C — Schedule/health | Daily full validation and sanitized health summary | At least one scheduled success on main; stale/missing-run detection exercised |
| D — Recovery | Bounded transient retry, cancellation, failure report, controlled rerun and operator runbook | Controlled failure, timeout, cancellation, notification and recovery evidence |
| E — Agent loop | Issue-scoped agent branch/PR proof, no write powers beyond branch/PR | One bounded test PR; merge/release/deploy impossible |
| F — Dedicated runner decision | Only if cloud runners demonstrably cannot meet a required use case | Independent server runner health/recovery proof, or documented no-runner-needed decision |

Do not begin Phase F just because a laptop runner exists or because a cloud job is slow. First check caching, job decomposition, GitHub-hosted runner class, timeouts and artifact transfer.

## 5. Acceptance gate — NOT READY until every item is evidenced

- [ ] Push and pull-request event workflows are active and pass on exact current heads.
- [ ] A scheduled workflow is active on the default branch and at least one real scheduled run succeeds.
- [ ] Concurrency is tested with controlled overlapping runs: same-PR supersession works; unrelated PRs do not cancel each other; stateful jobs do not overlap destructively.
- [ ] Timeout and cancellation are demonstrated in a controlled test and correctly reported.
- [ ] A transient retry succeeds within the defined cap; a permanent failure is not retried.
- [ ] A deliberate controlled failure produces a sanitized report with job names and run link only.
- [ ] Stale queued/in-progress and missing heartbeat detection is exercised; recovery/handoff is documented.
- [ ] Every workflow/job has explicit least-privilege permissions and explicit timeout.
- [ ] Branch protection, required checks, force-push/deletion restrictions are verified in repository settings.
- [ ] Actions usage, cadence and spending cap are checked with the owner/account settings.
- [ ] Runner inventory and limitations are known; any required server runner is independently healthy and has tested recovery.
- [ ] Operator runbook, artifact retention and notification delivery limitations are documented.
- [ ] A bounded issue-to-PR agent test is completed if authorized/available; the test proves it cannot merge or deploy.
- [ ] No prohibited scoring, ranking, backtest approval, production, broker/trading, capital allocation, auto-merge, release or deployment action occurred.

Until every checkbox above has evidence linked from a workflow run, commit, configuration or owner verification, report **NOT READY** and do not begin normal product development.

## 6. Monitoring report contract

Every monitoring pass, including no-change passes, reports:
1. AI Packs main SHA and latest CI state.
2. Every open PR, Draft/open state, mergeability, exact head SHA and latest exact-head checks.
3. Latest workflow runs, schedule freshness, failed/cancelled/stale jobs.
4. Verified runner/permissions/branch protection/billing information and explicit unknowns.
5. Safe/reversible GitHub actions taken during this pass.
6. Exactly one of: «در حال پیشرفت»، «منتظر اقدام کاربر» or «متوقف/مسدود».
7. If no owner action is needed: «فعلاً کاری از طرف تو لازم نیست». If needed, give one complete and safe instruction.

A GitHub Actions issue comment is not delivery to the ChatGPT conversation. ChatGPT conversation delivery requires a separate scheduled monitoring automation/connection; never claim that mobile push or chat delivery occurred unless the platform confirms it.

## 7. Explicit prohibitions

This infrastructure program must not:
- merge mobApp PR #6 without separate explicit owner authorization;
- merge any other PR automatically;
- publish to GHCR, create public releases, deploy or change production;
- access, print or transmit secret values;
- assume the laptop or its self-hosted runner is available;
- execute untrusted PR code on persistent self-hosted runners;
- start product/research/data work before the P0 gate is accepted;
- enable investment scoring/ranking, probability calibration, backtest approval, broker/trading or capital allocation.
