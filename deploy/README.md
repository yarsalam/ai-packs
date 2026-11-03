# استقرار AI Packs روی VPS یارسلام

## اصل استقرار

- سورس، Dockerfile، وابستگی‌ها، Compose و Workflow در GitHub باقی می‌مانند.
- GitHub Actions تصویرهای Docker را می‌سازد؛ VPS فقط imageهای GHCR را Pull و Run می‌کند.
- هیچ ZIP توزیع، checkout سورس یا پوشهٔ build روی VPS لازم نیست.
- فقط فایل env خصوصی هر Pack و volumeهای runtime/model روی VPS باقی می‌مانند.
- هیچ volume دیتابیس اصلی mobApp (MySQL/Redis/Qdrant) توسط Packها mount یا حذف نمی‌شود.

## نگاشت سرویس‌ها به چهار Pack

| Pack | Microservices | Gateway host port | Backend network aliases |
|---|---|---:|---|
| SEO | ai_seo, aeo_tracker, ai_backlink_quality, ai_seo_recommender, seo_embedded_ai | 9000 | ai_seo, aeo_tracker, ai_backlink_quality, ai_seo_recommender |
| Safety | ai_moderation, ai_verification, ai_image, safety_embedded_ai | 9001 | ai_moderation, ai_verification, ai_image |
| Revenue | ai_monetization, ai_revenue, ai_uplift, ai_feedback | 9002 | ai_monetization, ai_revenue, ai_uplift, ai_feedback |
| Matching | ml_service, matching_embedded_ai, personality, ai_assistant, ai_support, model_init job | 9003 | ml_service, personality, ai_assistant, ai_support |

The same upstream embedded_ai source is built into separate SEO, Safety, and Matching image variants because environment/model responsibilities differ. The ai_ops service in mobApp is outside these four Packs and is intentionally not deployed by this Pack workflow; it needs a separate operational/credential review.

## Docker network

Pack service containers attach to their isolated Compose network for internal Redis/service-to-service communication. Only the API-facing microservices and each Gateway also attach to the existing external Docker network yarsalam_network, so the NestJS backend can resolve the service aliases already used by .env.production.example.

Before starting any Pack, confirm that yarsalam_network exists on the VPS. Do not create a second network with a different name and do not change the production backend env until aliases have been verified.

## Model downloads and disk/RAM

- Images do not contain repository checkouts or temporary build contexts.
- Model assets remain in named Docker volumes and are downloaded on first start/inference. These are required runtime data, not disposable build cache.
- Safety DeepFace/NudeNet assets and embedding model downloads need outbound access to their upstream hosts. Verify inference, not only /health.
- Matching includes a one-shot model_init job to download sentiment/emotion models to a named volume.
- On this 7.8 GiB VPS, start and evaluate one Pack at a time. Do not enable every AI Pack at once until measured memory under real inference demonstrates sufficient headroom. Images can be published without running all services concurrently.

## Deployment secrets

Copy the matching deploy/env/*.env.example to a private VPS path outside the repository (for example /etc/yarsalam/ai-packs/<pack>.env). Generate unique values for REDIS_PASSWORD and that Pack's admin token. Never commit private env files or put license/admin tokens in a frontend.

For Matching, keep `IMAGE_TAG` set to the immutable tag used by the rest of the Pack, and `AI_ASSISTANT_IMAGE` set to the exact immutable tag for the independently published ai_assistant image. Do not change the global `IMAGE_TAG` merely to update ai_assistant.

## GitHub image publication

The general pack publishing workflow is manual after review/merge. It publishes commit-tagged images. For repeatable deployment, use exact immutable tags in the private env file. GHCR packages must either be made public for unauthenticated VPS pulls or be pulled using a read-only GitHub Packages credential.

### Update only Matching ai_assistant

The workflow `.github/workflows/publish-matching-ai-assistant.yml` builds and publishes only `matching-pack-ai-assistant`. It verifies `pandas==2.2.3` in the generated requirements and checks imports inside the built image before publishing. The workflow does not deploy to the VPS.

The runtime-only Compose override `deploy/compose/matching-ai-assistant-override.yaml` changes only the `ai_assistant` image. After the workflow has succeeded and the exact output tag has been reviewed, set `AI_ASSISTANT_IMAGE` in the private Matching env file. Then run from the existing runtime Compose directory (use the actual paths already installed on the VPS):

```bash
docker compose --env-file "$ENV_FILE" -p yarsalam-matching-pack \
  -f matching-pack.json -f matching-ai-assistant-override.yaml pull ai_assistant

docker compose --env-file "$ENV_FILE" -p yarsalam-matching-pack \
  -f matching-pack.json -f matching-ai-assistant-override.yaml \
  up -d --no-deps ai_assistant
```

The command is intentionally limited to `ai_assistant`; do not run a project-wide `up`, `down`, or build for this repair. Verify the container health and logs, then test the Matching gateway path. The previous image tag lacked pandas and is known to crash at import.

## Do not run

- docker system prune --volumes
- docker volume prune
- docker compose down -v
- any command that deletes mobApp MySQL, Redis, or Qdrant volumes.

Use each Pack's Compose file with its own env file and project identity. Never run a project-wide down from the mobApp or admin production project to manage an AI Pack.


## Admin-panel pack control agent and progressive RAM/function test

`scripts/ai_pack_control_agent.py` is a small host-side runtime control process. It is not mounted into the Admin web/backend containers and no Docker socket is exposed to those containers.

Fixed project allowlist:
- `matching-pack` → `yarsalam-matching-pack` / `matching-pack.json` / gateway 9003
- `seo-pack` → `yarsalam-seo-pack` / `seo-pack.json` / gateway 9000
- `revenue-pack` → `yarsalam-revenue-pack` / `revenue-pack.json` / gateway 9002
- `safety-pack` → `yarsalam-safety-pack` / `safety-pack.yaml` / gateway 9001

Operations are fixed: GET status/job, start/stop/test one allowlisted Pack, progressive test, and explicit-confirmation Stop All. The process binds only to the exact Docker bridge gateway IP of `yarsalam_network`, requires a 48+ character bearer token, serializes operations, and keeps actor/job reports in a private host directory.

Start behavior:
- Uses only existing immutable SHA-tagged local GHCR images and `docker compose up -d --no-recreate --pull never --wait`.
- Never builds or pulls images.
- Existing healthy containers are not recreated.
- During progressive tests, the order is Matching → SEO → Revenue → Safety. Not-installed Packs are reported/skipped.
- Memory is sampled through `/proc/meminfo` during Compose startup and functional tests. Initial guardrails: 2500 MiB before a start, 1536 MiB reserve after start/test, and 1024 MiB emergency floor during a long Compose operation. If a reserve/emergency guard is breached, only the newly-started Pack can be stopped; already-running Packs and mobApp/Admin infrastructure are preserved.
- Successful Packs are left running to measure cumulative memory. Stop All targets only the four fixed AI Pack Compose projects; it cannot stop mobapp, admin, MySQL, Redis, Qdrant, Nginx or volumes.

Functional tests call the existing `scripts/smoke_test_packs.py`:
- SEO checks gateway/dependencies, a public URL HTML audit (`https://example.com/`) and topical similarity. The URL audit result is reported as outbound/VPN egress unavailable when it fails; this does not prove VPN is the only possible cause. Enable the intended VPS VPN/outbound route before the SEO test if public URL auditing is expected to work.
- Revenue calls the promotion prediction endpoint and separately records `model_trained`, `cv_score`, `model_phase`, and `training_samples`. A working endpoint does not imply a trained or commercially validated model.
- Matching runs embedding and sentiment inference.
- Safety runs Persian text moderation examples. It is skipped until its images and private env file exist on VPS.
- Each smoke test creates a temporary test licence and revokes it; never substitute a real user licence/key.

Install on the VPS only after reviewing the PR and verifying the branch CI:
`bash scripts/install_ai_pack_control_agent.sh` is intentionally not a source build or repo checkout. It installs the two small runtime Python files under `~/.local/lib/yarsalam-ai-pack-control`, creates a private systemd unit and token, updates the existing private Admin `.env` with AI_PACK_CONTROL_URL/TOKEN (with a backup), and starts one progressive test. It does not update/restart the Admin backend/web container; the Admin runtime image/Compose changes are a separate reviewed deployment.

Do not run `down`, `--remove-orphans`, `down -v`, any prune, or project-wide build. Existing `yarsalam_network`, model volumes and DB volumes must be preserved.
