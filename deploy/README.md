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
