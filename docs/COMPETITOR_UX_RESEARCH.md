# Research notes: commercial Trust & Safety product UX

**Research date:** 2026-11-03  
**Scope:** Public product pages and documentation; this is a UX feature comparison, not a model-quality benchmark.

## Products reviewed

### Besedo / Implio
- Official site: https://besedo.com/
- Product positioning: hybrid AI + human moderation for marketplaces, dating, communities, gaming, publishers and other UGC platforms.
- Public dashboard reference: Besedo's Implio dashboard screenshot (moderation totals, approved/refused/no-decision, automation vs manual split, trend chart and awaiting manual review): https://besedo.com/wp-content-ext/uploads/2025/01/Implio-1200x978.webp
- UX elements to learn from: decision KPIs, automated vs manual breakdown, time range, activity trend and pending queue count.

### Hive Moderation Dashboard
- Official dashboard overview: https://docs.thehive.ai/docs/what-is-the-moderation-dashboard
- Review feed guide: https://docs.thehive.ai/docs/post-review-feed-1
- Screenshot reference: https://files.readme.io/91c708bf101f0b81c796b753f5b40401377c6693055ab988ef4630fe48d3a2be-moddash_review_feeds_6.png
- Documented capabilities: configurable automated actions, post/user rules, human review feeds, thresholds, role/access management, analytics/logs, appeals and alerts.
- UX elements to learn from: clear reason for flagging, content context, reviewer actions, queue filters and operator workload.

### Sightengine
- Official product: https://sightengine.com/
- Workflow guide: https://sightengine.com/faq/what-is-a-workflow
- Confidence thresholds: https://sightengine.com/faq/confidence-thresholds
- Screenshot references:
  - Rules editor: https://sightengine.com/assets/img/screenshot/workflow-screenshot.png
  - Threshold editor: https://sightengine.com/assets/img/doc/hybrid-moderation-thresholds.png
- Documented capabilities: custom workflows, category-level thresholds, accept/reject/review actions, image/video/text/audio moderation and profile-image checks.
- UX elements to learn from: editable policies, category-level actions and separate thresholds for automation vs review.

## Requirements for the YarSalam Safety workspace

The current product should be designed around the Trust & Safety operator's daily tasks, rather than a generic AI marketing page.

### Operator overview
- Total items processed, auto-approved, flagged for review, blocked and unresolved.
- Automated vs human decision split.
- Time range selector and activity trend.
- Category breakdown (spam, off-platform contact, abuse/harassment, threats, image safety, identity/profile).
- Clear state for missing data; never present sample values as real product metrics.

### Human review
- Separate queue for content and user/account reports.
- Item preview with safe context, content type, creation time and pseudonymous reference.
- Explicit reason the model/rule raised the item.
- Risk band and model signal, clearly labelled as uncalibrated until evaluation proves otherwise.
- Approve, reject, escalate and request-more-context actions.
- Filters for priority, category, age, reported items and assignee.
- Reviewer assignment, activity log and audit trail.
- Appeals and reversal workflow as a release requirement.

### Policy builder
- Per-category action: allow, review or block.
- Separate model threshold for auto action and human review.
- Tenant-specific phrase/domain/URL policies, with version and change history.
- Preview mode / test against a safe sample before saving.
- Roles/permissions and explicit publish/rollback.

### Analytics and operations
- Decision volume, reason breakdown, automation ratio and review backlog.
- Quality metrics only from a labelled, versioned and legally usable benchmark: precision, recall, F1, false-positive/negative rates and support counts.
- p50/p95 latency, request errors, throughput, per-operation cost and monthly credits.
- Model revision, pack version, upstream MobApp source SHA and CI status.
- Server CPU/RAM/disk only from a private authenticated control-agent connection.
- Retention, privacy and audit-log status.

## Current implementation status in the WordPress preview

The interactive demo now contains:
- overview KPI cards, weekly activity chart and flagged-category breakdown;
- recent items and a three-item human review queue;
- local-only allow/review/block actions;
- a three-category policy editor and local threshold slider;
- a read-only WordPress admin operations console showing public GitHub Actions runs.

All numbers and queue entries shown in the public preview are clearly marked as synthetic demo data. The admin console reports benchmark and resource data as unavailable until real measurement/secure private telemetry exists.

## Explicit non-goals for this preview

- It does not call the live moderation Gateway.
- It does not store or transmit user content.
- It does not expose the private control agent or its token.
- It does not claim that the current moderation model has commercial-grade accuracy.
- It does not enable the review, block or policy actions on live YarSalam users.
