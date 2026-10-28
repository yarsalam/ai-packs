# Model provenance and commercial release gates

**Snapshot reviewed:** 2026-10-28  
**Important:** License labels below are the current metadata shown on the linked model cards. They are not a legal opinion, and they do not automatically grant rights to redistribute every dependency, training dataset, or model artifact. Review the license file/model card at the exact pinned revision before public distribution.

## Models downloaded by the generated packs

| Pack/service | Model ID | Purpose | Current card metadata | Release status |
|---|---|---|---|---|
| SEO, Safety, Matching — embedding services | [sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) | Multilingual embeddings / similarity | Hugging Face card labels the model Apache-2.0 | Pin an immutable revision; benchmark Persian/Finglish queries |
| Matching — sentiment | [HooshvareLab/bert-fa-base-uncased-sentiment-snappfood](https://huggingface.co/HooshvareLab/bert-fa-base-uncased-sentiment-snappfood) | Persian sentiment classification | Card labels the model Apache-2.0; model card describes a SnappFood review dataset | Pin revision and check whether the customer-domain distribution is sufficiently similar |
| Matching — emotion | [aref-j/emotion-classifier-bert-fa-v1](https://huggingface.co/aref-j/emotion-classifier-bert-fa-v1) | Persian emotion classification | Card labels the model MIT; the card lists six emotion classes and reports author-run evaluation | Pin revision and reproduce metrics on an independent benchmark before making accuracy claims |
| Safety — face verification/image analysis | [DeepFace](https://github.com/serengil/deepface) and the [NudeNet project](https://github.com/notAI-tech/NudeNet) | Face comparison, image analysis and NSFW signals | Separate library/model terms apply; inspect the exact release and downloaded model artifacts | **Legal review required before public redistribution or managed-service claims** |

The Hugging Face card for the sentiment model currently states that it was evaluated on 70,000 SnappFood comments and reports F1 results for its own benchmark. That result is not a measurement of YarSalam's dating/social-platform messages, slang, Finglish, harassment or spam. Similarly, figures reported by the emotion model authors are not independently reproduced results for this product.

## Reproducibility requirements

The builder now supports `EMBEDDING_MODEL_REVISION`, `SENTIMENT_MODEL_REVISION` and `EMOTION_MODEL_REVISION`; the generated sample pins the embedding model to `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`, sentiment to `b6fcfc5`, and emotion to `e47c57d`. The sentiment/emotion refs are short immutable commit identifiers; verify they resolve at build time and record the resolved full commit SHA in the release manifest before public release. Apply the same rule to all model artifacts downloaded by DeepFace/NudeNet. Store selected IDs, revisions, licenses, checksums and download URLs in the final manifest.

## Required before calling a pack production-ready

1. Fix model IDs and immutable revisions; produce a manifest for every image/model artifact and its SHA-256 checksum.
2. Review model, dataset and library licenses with the planned hosting/redistribution model in mind.
3. Create a Persian evaluation set with documented consent/provenance; split by source/time and keep a sealed test set.
4. Publish per-task precision, recall, false-positive/false-negative rates, and representative limitations; do not use confidence scores as calibrated probabilities without calibration.
5. Test actual inference on the built containers (including offline/cold start, no model-cache, bad input, timeout and resource limits); building a Gateway image alone does not validate inference.
6. Publish data retention/deletion policy, privacy/security review, incident/rollback process and a clear human-review path for uncertain Safety results.

## Source cards reviewed

- [Persian SnappFood sentiment model](https://huggingface.co/HooshvareLab/bert-fa-base-uncased-sentiment-snappfood)
- [Persian emotion model](https://huggingface.co/aref-j/emotion-classifier-bert-fa-v1)
- [Multilingual embedding model](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
- [DeepFace source repository](https://github.com/serengil/deepface)
- [NudeNet source repository](https://github.com/notAI-tech/NudeNet)
