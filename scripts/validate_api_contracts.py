#!/usr/bin/env python3
"""Cross-check each Gateway proxy route against the original mobApp microservice route."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

CONTRACTS: list[dict[str, Any]] = [
    # SEO
    {"gateway":"seo-pack/gateway/main.py","handler":"seo_predict_traffic","service":"seo","target":'"/predict/traffic"',"source":"ai_seo/api/app.py","route":"/predict/traffic"},
    {"gateway":"seo-pack/gateway/main.py","handler":"seo_campaign_feedback","service":"seo","target":'"/feedback/campaign"',"source":"ai_seo/api/app.py","route":"/feedback/campaign"},
    {"gateway":"seo-pack/gateway/main.py","handler":"aeo_check_mentions","service":"aeo","target":'"/check-mentions"',"source":"ai_aeo_tracker/app.py","route":"/check-mentions"},
    {"gateway":"seo-pack/gateway/main.py","handler":"aeo_history","service":"aeo","target":'f"/history/{brand}"',"source":"ai_aeo_tracker/app.py","route":"/history/{brand}"},
    {"gateway":"seo-pack/gateway/main.py","handler":"backlink_trust_flow","service":"backlink","target":'"/trust-flow"',"source":"ai_backlink_quality/app.py","route":"/trust-flow"},
    {"gateway":"seo-pack/gateway/main.py","handler":"backlink_topic_similarity","service":"backlink","target":'"/topic-similarity"',"source":"ai_backlink_quality/app.py","route":"/topic-similarity"},
    {"gateway":"seo-pack/gateway/main.py","handler":"recommender_train","service":"recommend","target":'"/train"',"source":"ai_seo_recommender/app.py","route":"/train"},
    {"gateway":"seo-pack/gateway/main.py","handler":"recommender_recommend","service":"recommend","target":'"/recommend"',"source":"ai_seo_recommender/app.py","route":"/recommend"},
    # Safety
    {"gateway":"safety-pack/gateway/main.py","handler":"moderate_text","service":"moderation","target":'"/moderate"',"source":"ai_moderation/app.py","route":"/moderate"},
    {"gateway":"safety-pack/gateway/main.py","handler":"moderate_batch","service":"moderation","target":'"/moderate/batch"',"source":"ai_moderation/app.py","route":"/moderate/batch"},
    {"gateway":"safety-pack/gateway/main.py","handler":"verify_face","service":"verification","target":'"/verify"',"source":"ai_verification/app.py","route":"/verify"},
    {"gateway":"safety-pack/gateway/main.py","handler":"image_upload","service":"image","target":'"/image/upload"',"source":"ai_image/app.py","route":"/image/upload"},
    {"gateway":"safety-pack/gateway/main.py","handler":"image_analyze","service":"image","target":'"/image/analyze"',"source":"ai_image/app.py","route":"/image/analyze"},
    {"gateway":"safety-pack/gateway/main.py","handler":"image_status","service":"image","target":'f"/image/status/{filename}"',"source":"ai_image/app.py","route":"/image/status/{filename}"},
    # Revenue
    {"gateway":"revenue-pack/gateway/main.py","handler":"predict_promotion","service":"monetization","target":'"/api/predict-promotion"',"source":"ai_monetization/routes/promotion.py","route":"/predict-promotion","prefix_file":"ai_monetization/app.py","prefix":"/api"},
    {"gateway":"revenue-pack/gateway/main.py","handler":"monetization_feedback","service":"monetization","target":'"/api/feedback"',"source":"ai_monetization/routes/promotion.py","route":"/feedback","prefix_file":"ai_monetization/app.py","prefix":"/api"},
    {"gateway":"revenue-pack/gateway/main.py","handler":"monetization_retrain","service":"monetization","target":'"/api/retrain-from-feedback"',"source":"ai_monetization/routes/promotion.py","route":"/retrain-from-feedback","prefix_file":"ai_monetization/app.py","prefix":"/api"},
    {"gateway":"revenue-pack/gateway/main.py","handler":"predict_ltv","service":"revenue","target":'"/predict/ltv"',"source":"ai_revenue/app.py","route":"/predict/ltv"},
    {"gateway":"revenue-pack/gateway/main.py","handler":"train_revenue_model","service":"revenue","target":'"/train"',"source":"ai_revenue/app.py","route":"/train"},
    {"gateway":"revenue-pack/gateway/main.py","handler":"train_uplift","service":"uplift","target":'"/train"',"source":"ai_uplift/app.py","route":"/train"},
    {"gateway":"revenue-pack/gateway/main.py","handler":"predict_uplift","service":"uplift","target":'"/predict-uplift"',"source":"ai_uplift/app.py","route":"/predict-uplift"},
    {"gateway":"revenue-pack/gateway/main.py","handler":"train_feedback","service":"feedback","target":'"/feedback/train_incremental"',"source":"ai_feedback/app.py","route":"/feedback/train_incremental"},
    {"gateway":"revenue-pack/gateway/main.py","handler":"train_feedback_batch","service":"feedback","target":'"/feedback/train_batch"',"source":"ai_feedback/app.py","route":"/feedback/train_batch"},
    {"gateway":"revenue-pack/gateway/main.py","handler":"predict_conversion","service":"feedback","target":'"/feedback/predict"',"source":"ai_feedback/app.py","route":"/feedback/predict"},
    {"gateway":"revenue-pack/gateway/main.py","handler":"feedback_metrics","service":"feedback","target":'"/feedback/metrics"',"source":"ai_feedback/app.py","route":"/feedback/metrics"},
    # Matching, embeddings, assistant and support
    {"gateway":"matching-pack/gateway/main.py","handler":"match_embed","service":"match","target":'"/api/embed"',"source":"ml_service/routes/matching.py","route":"/embed","prefix_file":"ml_service/app.py","prefix":"/api"},
    {"gateway":"matching-pack/gateway/main.py","handler":"match_recommend","service":"match","target":'"/api/recommend"',"source":"ml_service/routes/matching.py","route":"/recommend","prefix_file":"ml_service/app.py","prefix":"/api"},
    {"gateway":"matching-pack/gateway/main.py","handler":"match_predict","service":"match","target":'"/api/predict"',"source":"ml_service/routes/matching.py","route":"/predict","prefix_file":"ml_service/app.py","prefix":"/api"},
    {"gateway":"matching-pack/gateway/main.py","handler":"match_track_events","service":"match","target":'"/api/internal/track-events"',"source":"ml_service/routes/matching.py","route":"/internal/track-events","prefix_file":"ml_service/app.py","prefix":"/api"},
    {"gateway":"matching-pack/gateway/main.py","handler":"embed_text","service":"embed","target":'"/embed"',"source":"embedded_ai/app.py","route":"/embed"},
    {"gateway":"matching-pack/gateway/main.py","handler":"embed_batch","service":"embed","target":'"/embed/batch"',"source":"embedded_ai/app.py","route":"/embed/batch"},
    {"gateway":"matching-pack/gateway/main.py","handler":"embed_similarity","service":"embed","target":'"/similarity"',"source":"embedded_ai/app.py","route":"/similarity"},
    {"gateway":"matching-pack/gateway/main.py","handler":"personality_sentiment","service":"personality","target":'"/analyze_sentiment"',"source":"personality/main.py","route":"/analyze_sentiment"},
    {"gateway":"matching-pack/gateway/main.py","handler":"personality_emotion","service":"personality","target":'"/analyze_emotion"',"source":"personality/main.py","route":"/analyze_emotion"},
    {"gateway":"matching-pack/gateway/main.py","handler":"assistant_analyze","service":"assistant","target":'"/api/assistant/analyze"',"source":"ai_assistant/api/assistant.py","route":"/analyze","prefix_file":"ai_assistant/app.py","prefix":"/api/assistant"},
    {"gateway":"matching-pack/gateway/main.py","handler":"assistant_advice","service":"assistant","target":'f"/api/assistant/advice/{user_id}"',"source":"ai_assistant/api/assistant.py","route":"/advice/{user_id}","prefix_file":"ai_assistant/app.py","prefix":"/api/assistant"},
    {"gateway":"matching-pack/gateway/main.py","handler":"assistant_chat","service":"assistant","target":'"/api/assistant/chat"',"source":"ai_assistant/api/assistant.py","route":"/chat","prefix_file":"ai_assistant/app.py","prefix":"/api/assistant"},
    {"gateway":"matching-pack/gateway/main.py","handler":"support_analyze","service":"support","target":'"/api/analyze"',"source":"ai_support/api/app.py","route":"/api/analyze"},
    {"gateway":"matching-pack/gateway/main.py","handler":"support_get_analysis","service":"support","target":'f"/api/tickets/{ticket_id}/analysis"',"source":"ai_support/api/app.py","route":"/api/tickets/{ticket_id}/analysis"},
    {"gateway":"matching-pack/gateway/main.py","handler":"support_feedback","service":"support","target":'"/api/feedback"',"source":"ai_support/api/app.py","route":"/api/feedback"},
    {"gateway":"matching-pack/gateway/main.py","handler":"support_seo_insights","service":"support","target":'"/api/seo-insights"',"source":"ai_support/api/app.py","route":"/api/seo-insights"},
]


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"Missing required contract file: {path}")
    return path.read_text(encoding="utf-8")


def route_decorator_present(content: str, route: str) -> bool:
    escaped = re.escape(route)
    pattern = rf'@(app|router)\.(get|post|put|patch|delete)\(\s*f?["\']{escaped}["\']'
    return re.search(pattern, content) is not None


def function_body(gateway_content: str, handler: str) -> str:
    match = re.search(rf"async def {re.escape(handler)}\s*\(", gateway_content)
    if not match:
        raise ValueError(f"Gateway handler not found: {handler}")
    start = match.start()
    ends = [pos for token in ("\n@app.", "\nasync def ") if (pos := gateway_content.find(token, match.end())) >= 0]
    end = min(ends) if ends else len(gateway_content)
    return gateway_content[start:end]


def validate_contract(root: Path, item: dict[str, Any]) -> None:
    gateway_path = root / item["gateway"]
    gateway_content = read(gateway_path)
    body = function_body(gateway_content, item["handler"])
    if item["service"] not in body or item["target"] not in body:
        raise ValueError(
            f"{item['gateway']}::{item['handler']} does not proxy to "
            f"{item['service']} at {item['target']}"
        )

    source_path = root / "upstream" / item["source"]
    source_content = read(source_path)
    if not route_decorator_present(source_content, item["route"]):
        raise ValueError(f"Source route {item['route']} not found in {source_path}")

    if "prefix" in item:
        prefix_file = root / "upstream" / item["prefix_file"]
        prefix_content = read(prefix_file)
        prefix_pattern = rf'include_router\([^)]*prefix\s*=\s*["\']{re.escape(item["prefix"])}["\']'
        if not re.search(prefix_pattern, prefix_content, flags=re.S):
            raise ValueError(
                f"Expected router prefix {item['prefix']} not found in {prefix_file}"
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ai-packs-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--mobapp-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.ai_packs_root.resolve()
    upstream = args.mobapp_root.resolve()

    failures = []
    for item in CONTRACTS:
        item_root = dict(item)
        try:
            # Gateway paths live in this repository; source paths are resolved from mobApp.
            gateway_content = read(root / item["gateway"])
            body = function_body(gateway_content, item["handler"])
            if item["service"] not in body or item["target"] not in body:
                raise ValueError(
                    f"{item['gateway']}::{item['handler']} does not proxy to "
                    f"{item['service']} at {item['target']}"
                )
            source_content = read(upstream / "python-ai/services" / item["source"])
            if not route_decorator_present(source_content, item["route"]):
                raise ValueError(f"Source route {item['route']} not found in {item['source']}")
            if "prefix" in item:
                prefix_content = read(upstream / "python-ai/services" / item["prefix_file"])
                prefix_pattern = rf'include_router\([^)]*prefix\s*=\s*["\']{re.escape(item["prefix"])}["\']'
                if not re.search(prefix_pattern, prefix_content, flags=re.S):
                    raise ValueError(f"Expected router prefix {item['prefix']} missing in {item['prefix_file']}")
        except (ValueError, SystemExit) as exc:
            failures.append(str(exc))

    if failures:
        raise SystemExit("\n".join(f"- {failure}" for failure in failures))
    print(f"Validated {len(CONTRACTS)} Gateway-to-microservice API route contracts.")


if __name__ == "__main__":
    main()
