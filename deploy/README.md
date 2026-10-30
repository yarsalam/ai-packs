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

## GitHub image publication

The publishing workflow is manual after review/merge. It tags images with both latest and sha-<full-commit>. For repeatable deployment, set IMAGE_TAG to the exact SHA tag in the Pack's private env file. GHCR packages must either be made public for unauthenticated VPS pulls or be pulled using a read-only GitHub Packages credential.

## Do not run

- docker system prune --volumes
- docker volume prune
- docker compose down -v
- any command that deletes mobApp MySQL, Redis, or Qdrant volumes.

Use each Pack's Compose file with its own env file and project identity. Never run a project-wide down from the mobApp or admin production project to manage an AI Pack.
