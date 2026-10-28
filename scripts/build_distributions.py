#!/usr/bin/env python3
"""Build stand-alone AI Pack distributions from a checkout of yarsalam/mobApp."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PYTHON_BASE = "python:3.11-slim"
DOLLAR = "$"

CORE = [
    "fastapi==0.115.12", "uvicorn[standard]==0.34.0", "pydantic==2.10.6",
    "python-multipart==0.0.20", "redis==5.2.1", "httpx==0.28.1", "python-dotenv==1.0.1",
]
TORCH_CPU = [
    "--extra-index-url https://download.pytorch.org/whl/cpu",
    "torch==2.6.0+cpu", "transformers==4.49.0", "tokenizers==0.21.0",
    "safetensors==0.5.3", "accelerate==1.4.0",
]
ST_SENTENCE = [
    "--extra-index-url https://download.pytorch.org/whl/cpu",
    "torch==2.6.0+cpu", "sentence-transformers==3.4.1", "transformers==4.49.0",
    "tokenizers==0.21.0", "safetensors==0.5.3", "accelerate==1.4.0", "numpy==1.26.4",
]
REDIS_URL = "redis://:" + DOLLAR + "{REDIS_PASSWORD}@redis:6379/0"

SERVICE: dict[str, dict[str, Any]] = {
    "ai_seo": {
        "source": "ai_seo", "port": 8021, "entrypoint": "api.app:app",
        "requirements": CORE + ["numpy==1.26.4", "pandas==2.2.3", "scikit-learn==1.6.1", "prophet==1.1.6", "beautifulsoup4==4.13.3", "joblib==1.4.2", "apscheduler==3.11.0"],
        "env": {"REDIS_HOST": "redis", "REDIS_PORT": "6379", "REDIS_PASSWORD": DOLLAR + "{REDIS_PASSWORD}", "MODEL_PATH": "/app/models"},
        "volumes": {"seo_models": "/app/models"}, "depends": ["redis"],
    },
    "aeo_tracker": {
        "source": "ai_aeo_tracker", "port": 8030, "entrypoint": "app:app",
        "requirements": CORE + ["openai==1.65.5"],
        "env": {"REDIS_URL": REDIS_URL, "REDIS_HOST": "redis", "REDIS_PORT": "6379", "REDIS_PASSWORD": DOLLAR + "{REDIS_PASSWORD}", "OPENAI_API_KEY": DOLLAR + "{OPENAI_API_KEY:-}"},
        "volumes": {}, "depends": ["redis"],
    },
    "ai_backlink_quality": {
        "source": "ai_backlink_quality", "port": 8032, "entrypoint": "app:app",
        "requirements": CORE + ["networkx==3.4.2"],
        "env": {"EMBEDDING_SERVICE_URL": "http://seo_embedded_ai:8100"},
        "volumes": {}, "depends": ["seo_embedded_ai"],
    },
    "ai_seo_recommender": {
        "source": "ai_seo_recommender", "port": 8033, "entrypoint": "app:app",
        "requirements": CORE + ["numpy==1.26.4", "scipy==1.15.2", "implicit==0.7.2", "joblib==1.4.2"],
        "env": {"CF_MODEL_PATH": "/app/models/cf_model.pkl"},
        "volumes": {"seo_recommender_models": "/app/models"}, "depends": [],
    },
    "seo_embedded_ai": {
        "source": "embedded_ai", "port": 8100, "entrypoint": "app:app",
        "requirements": CORE + ST_SENTENCE,
        "env": {"REDIS_URL": REDIS_URL, "MODEL_NAME": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "HF_HOME": "/models/huggingface"},
        "volumes": {"seo_embedding_models": "/models"}, "depends": ["redis"],
    },
    "ai_moderation": {
        "source": "ai_moderation", "port": 8018, "entrypoint": "app:app",
        "requirements": CORE,
        "env": {"EMBEDDING_SERVICE_URL": "http://safety_embedded_ai:8100"},
        "volumes": {}, "depends": ["safety_embedded_ai"],
    },
    "ai_verification": {
        "source": "ai_verification", "port": 8017, "entrypoint": "app:app",
        "requirements": CORE + ["numpy==1.26.4", "tensorflow==2.18.0", "tf-keras==2.18.0", "deepface==0.0.93", "opencv-python==4.11.0.86", "Pillow==11.1.0"],
        "env": {"VERIFICATION_THRESHOLD": "0.4", "HOME": "/models"},
        "volumes": {"safety_verification_models": "/models"}, "depends": [],
    },
    "ai_image": {
        "source": "ai_image", "port": 8100, "entrypoint": "app:app",
        "requirements": CORE + ["numpy==1.26.4", "tensorflow==2.18.0", "tf-keras==2.18.0", "deepface==0.0.93", "opencv-python==4.11.0.86", "Pillow==11.1.0", "nudenet==3.4.2"],
        "env": {"REDIS_URL": REDIS_URL, "HOME": "/models", "MAX_IMAGE_BYTES": "10485760"},
        "volumes": {"safety_image_models": "/models"}, "depends": ["redis"],
    },
    "safety_embedded_ai": {
        "source": "embedded_ai", "port": 8100, "entrypoint": "app:app",
        "requirements": CORE + ST_SENTENCE,
        "env": {"REDIS_URL": REDIS_URL, "MODEL_NAME": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "HF_HOME": "/models/huggingface"},
        "volumes": {"safety_embedding_models": "/models"}, "depends": ["redis"],
    },
    "ai_monetization": {
        "source": "ai_monetization", "port": 8015, "entrypoint": "app:app",
        "requirements": CORE + ["numpy==1.26.4", "scikit-learn==1.5.2", "xgboost==2.1.4", "joblib==1.4.2"],
        "env": {"REDIS_URL": REDIS_URL, "MODEL_PATH": "/app/models", "MODEL_VERSION": "v1"},
        "volumes": {"monetization_models": "/app/models"}, "depends": ["redis"],
    },
    "ai_revenue": {
        "source": "ai_revenue", "port": 8000, "entrypoint": "app:app",
        "requirements": CORE + ["numpy==1.26.4", "pandas==2.2.3", "scikit-learn==1.5.2", "joblib==1.4.2"],
        "env": {"MODEL_DIR": "/app/models"},
        "volumes": {"revenue_models": "/app/models"}, "depends": [],
    },
    "ai_uplift": {
        "source": "ai_uplift", "port": 8031, "entrypoint": "app:app",
        "requirements": CORE + ["numpy==1.26.4", "pandas==2.2.3", "scikit-learn==1.5.2", "econml==0.15.1", "dowhy==0.12"],
        "env": {"UPLIFT_MODEL_PATH": "/app/models/uplift_model.pkl"},
        "volumes": {"uplift_models": "/app/models"}, "depends": [],
    },
    "ai_feedback": {
        "source": "ai_feedback", "port": 8004, "entrypoint": "app:app",
        "requirements": CORE + ["numpy==1.26.4", "pandas==2.2.3", "scikit-learn==1.5.2", "joblib==1.4.2"],
        "env": {"MODEL_PATH": "/app/models/conversion_model.pkl"},
        "volumes": {"feedback_models": "/app/models"}, "depends": [],
    },
    "ml_service": {
        "source": "ml_service", "port": 8000, "entrypoint": "app:app",
        "requirements": CORE + ["numpy==1.26.4", "pydantic-settings==2.8.1"],
        "env": {"REDIS_URL": REDIS_URL, "EMBEDDING_SERVICE_URL": "http://matching_embedded_ai:8100"},
        "volumes": {"matching_ml_models": "/app/models"}, "depends": ["redis", "matching_embedded_ai"],
    },
    "matching_embedded_ai": {
        "source": "embedded_ai", "port": 8100, "entrypoint": "app:app",
        "requirements": CORE + ST_SENTENCE,
        "env": {"REDIS_URL": REDIS_URL, "MODEL_NAME": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "HF_HOME": "/models/huggingface"},
        "volumes": {"matching_embedding_models": "/models"}, "depends": ["redis"],
    },
    "personality": {
        "source": "personality", "port": 8100, "entrypoint": "main:app",
        "requirements": CORE + TORCH_CPU,
        "env": {"TRANSFORMERS_OFFLINE": "1", "HF_HOME": "/models/huggingface-cache"},
        "volumes": {"matching_personality_models": "/models"}, "depends": ["model_init"],
    },
    "ai_assistant": {
        "source": "ai_assistant", "port": 8022, "entrypoint": "app:app",
        "requirements": CORE + TORCH_CPU,
        "env": {"REDIS_URL": REDIS_URL, "TRANSFORMERS_OFFLINE": "1", "SENTIMENT_MODEL": "/models/sentiment", "HF_HOME": "/models/huggingface-cache"},
        "volumes": {"matching_personality_models": "/models", "assistant_models": "/app/models"}, "depends": ["redis", "model_init"],
    },
    "ai_support": {
        "source": "ai_support", "port": 8016, "entrypoint": "api.app:app",
        "requirements": CORE + TORCH_CPU,
        "env": {"REDIS_URL": REDIS_URL, "MODEL_PATH": "/models/sentiment", "TRANSFORMERS_OFFLINE": "1", "HF_HOME": "/models/huggingface-cache"},
        "volumes": {"matching_personality_models": "/models"}, "depends": ["redis", "model_init"],
    },
}

PACKS: dict[str, dict[str, Any]] = {
    "seo-pack": {
        "label": "SEO Pack", "port": 9000, "admin_env": "SEO_PACK_ADMIN_TOKEN", "rate": 500,
        "gateway_services": {"AI_SEO_URL": "ai_seo", "AEO_TRACKER_URL": "aeo_tracker", "AI_BACKLINK_URL": "ai_backlink_quality", "AI_RECOMMENDER_URL": "ai_seo_recommender"},
        "services": ["ai_seo", "aeo_tracker", "ai_backlink_quality", "ai_seo_recommender", "seo_embedded_ai"],
        "plugin": ("seo-pack/wordpress-plugin/seo-pack", "seo-pack"), "readme": "seo-pack/README.md",
    },
    "safety-pack": {
        "label": "Safety Pack", "port": 9001, "admin_env": "SAFETY_PACK_ADMIN_TOKEN", "rate": 1000,
        "gateway_services": {"AI_MODERATION_URL": "ai_moderation", "AI_VERIFICATION_URL": "ai_verification", "AI_IMAGE_URL": "ai_image"},
        "services": ["ai_moderation", "ai_verification", "ai_image", "safety_embedded_ai"],
        "plugin": ("safety-pack/wordpress-plugin/safety-pack", "safety-pack"), "readme": "safety-pack/README.md",
    },
    "revenue-pack": {
        "label": "Revenue Pack", "port": 9002, "admin_env": "REVENUE_PACK_ADMIN_TOKEN", "rate": 2000,
        "gateway_services": {"AI_MONETIZATION_URL": "ai_monetization", "AI_REVENUE_URL": "ai_revenue", "AI_UPLIFT_URL": "ai_uplift", "AI_FEEDBACK_URL": "ai_feedback"},
        "services": ["ai_monetization", "ai_revenue", "ai_uplift", "ai_feedback"],
        "plugin": ("revenue-pack/wordpress-plugin/revenue-pack", "revenue-pack"), "readme": "revenue-pack/README.md",
    },
    "matching-pack": {
        "label": "Matching Pack", "port": 9003, "admin_env": "MATCHING_PACK_ADMIN_TOKEN", "rate": 3000, "model_init": True,
        "gateway_services": {"ML_SERVICE_URL": "ml_service", "EMBEDDED_AI_URL": "matching_embedded_ai", "PERSONALITY_URL": "personality", "AI_ASSISTANT_URL": "ai_assistant", "AI_SUPPORT_URL": "ai_support"},
        "services": ["ml_service", "matching_embedded_ai", "personality", "ai_assistant", "ai_support"],
        "plugin": ("matching-pack/wordpress-plugin/matching-pack", "matching-pack"), "readme": "matching-pack/README.md",
    },
}

COMMON_APT = ["build-essential", "curl", "libgl1", "libglib2.0-0", "libsm6", "libxext6", "libxrender1", "libgomp1"]
MODEL_INIT_DOCKERFILE = """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY download_models.py .
CMD ["python", "download_models.py"]
"""
MODEL_INIT_REQUIREMENTS = "\n".join([
    "--extra-index-url https://download.pytorch.org/whl/cpu", "torch==2.6.0+cpu",
    "transformers==4.49.0", "tokenizers==0.21.0", "safetensors==0.5.3", "accelerate==1.4.0",
]) + "\n"
MODEL_INIT_SCRIPT = '''import os
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification

DEST = Path("/models")
MODELS = {
    "sentiment": os.getenv("SENTIMENT_MODEL_ID", "HooshvareLab/bert-fa-base-uncased-sentiment-snappfood"),
    "emotion": os.getenv("EMOTION_MODEL_ID", "aref-j/emotion-classifier-bert-fa-v1"),
}
for name, model_id in MODELS.items():
    target = DEST / name
    if (target / "config.json").exists():
        print(f"{name}: already initialized from {model_id}", flush=True)
        continue
    print(f"Downloading {model_id} -> {target}", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(model_id)
    target.mkdir(parents=True, exist_ok=True)
    tokenizer.save_pretrained(target)
    model.save_pretrained(target)
    print(f"{name}: ready", flush=True)
'''

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def dockerfile(spec: dict[str, Any]) -> str:
    apt = " ".join(COMMON_APT)
    cmd = json.dumps(["uvicorn", spec["entrypoint"], "--host", "0.0.0.0", "--port", str(spec["port"]), "--workers", "1"])
    return (
        f"FROM {PYTHON_BASE}\n"
        "ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1\n"
        "WORKDIR /app\n"
        f"RUN apt-get update && apt-get install -y --no-install-recommends {apt} "
        "&& rm -rf /var/lib/apt/lists/*\n"
        "COPY requirements.txt .\n"
        "RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt\n"
        "COPY . .\nENV PYTHONPATH=/app\n"
        f"EXPOSE {spec['port']}\n"
        f"HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 CMD curl -fsS http://127.0.0.1:{spec['port']}/health || exit 1\n"
        f"CMD {cmd}\n"
    )

def required_env(name: str, message: str) -> str:
    return DOLLAR + "{" + name + ":?" + message + "}"

def volume_map(compose: dict[str, Any], spec: dict[str, Any], service_name: str) -> list[str]:
    result = []
    for vol, mount in spec.get("volumes", {}).items():
        compose["volumes"].setdefault(vol, {})
        read_only = vol == "matching_personality_models" and service_name in {"personality", "ai_assistant", "ai_support"}
        result.append(f"{vol}:{mount}" + (":ro" if read_only else ""))
    return result

def build_compose(pack_name: str, pack: dict[str, Any]) -> dict[str, Any]:
    name_expr = DOLLAR + "{COMPOSE_PROJECT_NAME:-yarsalam-" + pack_name + "}"
    redis_password_length = DOLLAR + DOLLAR + "{#REDIS_PASSWORD}"
    redis_password_value = DOLLAR + DOLLAR + "{REDIS_PASSWORD}"
    redis_start_command = (
        '[ "' + redis_password_length + '" -ge 32 ] || { echo "REDIS_PASSWORD must be at least 32 characters" >&2; exit 1; }; '
        'exec redis-server --appendonly yes --requirepass "' + redis_password_value + '"'
    )
    compose: dict[str, Any] = {"name": name_expr, "services": {}, "volumes": {"redis_data": {}}}
    compose["services"]["redis"] = {
        "image": "redis:7.4-alpine",
        "restart": "unless-stopped",
        "command": ["sh", "-ec", redis_start_command],
        "environment": {"REDIS_PASSWORD": required_env("REDIS_PASSWORD", "Set REDIS_PASSWORD in .env")},
        "volumes": ["redis_data:/data"],
        "healthcheck": {"test": ["CMD-SHELL", 'redis-cli --no-auth-warning -a "$$REDIS_PASSWORD" ping | grep -q PONG'], "interval": "10s", "timeout": "5s", "retries": 5, "start_period": "5s"},
    }
    for service_name in pack["services"]:
        spec = SERVICE[service_name]
        env = dict(spec.get("env", {}))
        for key, val in list(env.items()):
            if val == DOLLAR + "{REDIS_PASSWORD}":
                env[key] = required_env("REDIS_PASSWORD", "Set REDIS_PASSWORD in .env")
        if service_name == "ai_seo":
            env["REDIS_PASSWORD"] = required_env("REDIS_PASSWORD", "Set REDIS_PASSWORD in .env")
        service: dict[str, Any] = {
            "build": {"context": "./services/" + service_name},
            "restart": "unless-stopped",
            "init": True,
            "environment": env,
            "healthcheck": {"test": ["CMD", "curl", "-fsS", f"http://127.0.0.1:{spec['port']}/health"], "interval": "30s", "timeout": "5s", "retries": 3, "start_period": "120s"},
        }
        deps: dict[str, Any] = {}
        for dep in spec.get("depends", []):
            if dep == "redis":
                deps[dep] = {"condition": "service_healthy"}
            elif dep == "model_init":
                deps[dep] = {"condition": "service_completed_successfully"}
            else:
                deps[dep] = {"condition": "service_started"}
        if deps:
            service["depends_on"] = deps
        vols = volume_map(compose, spec, service_name)
        if vols:
            service["volumes"] = vols
        compose["services"][service_name] = service

    if pack.get("model_init"):
        compose["volumes"].setdefault("matching_personality_models", {})
        compose["services"]["model_init"] = {
            "build": {"context": "./model-init"}, "restart": "no",
            "environment": {"HF_HOME": "/models/huggingface-cache",
                            "SENTIMENT_MODEL_ID": "HooshvareLab/bert-fa-base-uncased-sentiment-snappfood",
                            "EMOTION_MODEL_ID": "aref-j/emotion-classifier-bert-fa-v1"},
            "volumes": ["matching_personality_models:/models"],
        }
        for service_name in ("personality", "ai_assistant", "ai_support"):
            compose["services"][service_name].setdefault("depends_on", {})["model_init"] = {"condition": "service_completed_successfully"}

    gateway_env = {
        "REDIS_URL": "redis://:" + required_env("REDIS_PASSWORD", "Set REDIS_PASSWORD in .env") + "@redis:6379/0",
        "ADMIN_TOKEN": required_env(pack["admin_env"], "Set " + pack["admin_env"] + " to a random secret of at least 32 characters"),
        "RATE_LIMIT_PER_HOUR": str(pack["rate"]),
    }
    for env_name, service_name in pack["gateway_services"].items():
        gateway_env[env_name] = f"http://{service_name}:{SERVICE[service_name]['port']}"
    gateway = {
        "build": {"context": "./gateway"},
        "restart": "unless-stopped",
        "init": True,
        "ports": [f"127.0.0.1:{pack['port']}:8000"],
        "environment": gateway_env,
        "depends_on": {name: {"condition": "service_started"} for name in pack["services"]},
        "healthcheck": {"test": ["CMD", "curl", "-fsS", "http://127.0.0.1:8000/health"], "interval": "30s", "timeout": "5s", "retries": 3, "start_period": "60s"},
    }
    compose["services"]["gateway"] = gateway
    return compose

def readme_for(pack_name: str, pack: dict[str, Any]) -> str:
    admin_env = pack["admin_env"]
    port = pack["port"]
    return f"""# {pack['label']} — توزیع مستقل

این بسته شامل Gateway، سرویس‌های Python موردنیاز و افزونهٔ WordPress است. برای ساخت/اجرای سرویس‌ها به مسیرهای خارج از همین پوشه وابسته نیست.

## نصب

1. Docker Engine و Docker Compose v2 را نصب کنید.
2. در همین پوشه اجرا کنید:

    cp .env.example .env

3. برای REDIS_PASSWORD و {admin_env} مقادیر تصادفی قوی بسازید (مثلاً خروجی openssl rand -hex 32) و در .env قرار دهید. از مقادیر نمونه استفاده نکنید.
4. اجرا کنید:

    docker compose --env-file .env up -d --build
    docker compose --env-file .env ps
    docker compose --env-file .env logs -f gateway

در اجرای اول، مدل‌های embedding و مدل‌های فارسی (در صورت نیاز این پک) از منبع اصلی دانلود می‌شوند؛ برای اجرای اولیه اتصال شبکه و فضای دیسک کافی لازم است.

## سلامت سرویس

    curl -fsS http://127.0.0.1:{port}/health

## صدور کلید آزمایشی

    curl -X POST http://127.0.0.1:{port}/admin/license/create \\
      -H "X-Admin-Token: ${admin_env}" \\
      -H "Content-Type: application/json" \\
      -d '{{"domain":"customer.example","plan":"pro","expires":"2027-12-31"}}'

کلید را فقط در backend مشتری ذخیره کنید و برای هر درخواست با هدر X-License-Key بفرستید. سهمیهٔ مصرف از GET /usage قابل مشاهده است. آموزش مدل فقط برای پلن‌های Pro و Enterprise فعال است.

## وضعیت تجاری

- سهمیه‌های اولیه برحسب credit در هر ساعت و ماه فعلاً فرضیه‌اند؛ باید پس از سنجش هزینهٔ واقعی inference و پایلوت مشتری تنظیم شوند.
- صدور/لغو مجوز فعلاً دستی و از API مدیریتی انجام می‌شود؛ پرداخت، پنل مشتری، تمدید خودکار و صدور مجوز پس از پرداخت هنوز به درگاه تجاری متصل نشده‌اند.
- API را با HTTPS و reverse proxy منتشر کنید؛ کلیدهای مدیریتی و License را در مرورگر یا اپ موبایل قرار ندهید.
- برای ادعای دقت، کاهش تقلب یا افزایش درآمد، ابتدا benchmark و ارزیابی مستقل روی دادهٔ نماینده انجام دهید.

## منشأ و مجوز مدل‌ها

کد سرویس‌ها از yarsalam/mobApp کپی شده است. manifest.json هش SHA-256 فایل‌های بسته را ثبت می‌کند. وزن مدل‌ها داخل repository ذخیره نمی‌شوند و در زمان نصب دریافت می‌شوند؛ پیش از توزیع عمومی، مجوز هر مدل و کتابخانه را بازبینی کنید.
"""

def build_one(pack_name: str, pack: dict[str, Any], upstream: Path, output: Path) -> Path:
    dist = output / pack_name
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir(parents=True)
    shutil.copytree(ROOT / pack_name / "gateway", dist / "gateway")
    plugin_source, plugin_slug = pack["plugin"]
    shutil.copytree(ROOT / plugin_source, dist / "wordpress-plugin" / plugin_slug)
    gd = dist / "gateway" / "Dockerfile"
    gateway_dockerfile = gd.read_text(encoding="utf-8")
    if "apt-get install" not in gateway_dockerfile:
        gateway_dockerfile = gateway_dockerfile.replace(
            "WORKDIR /app",
            "RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*\n\nWORKDIR /app",
        )
    gd.write_text(gateway_dockerfile, encoding="utf-8")

    for service_name in pack["services"]:
        spec = SERVICE[service_name]
        source = upstream / "python-ai" / "services" / spec["source"]
        if not source.is_dir():
            raise FileNotFoundError(f"Missing upstream service source: {source}")
        target = dist / "services" / service_name
        shutil.copytree(source, target)
        requirements = list(dict.fromkeys(spec["requirements"]))
        (target / "requirements.txt").write_text("\n".join(requirements) + "\n", encoding="utf-8")
        (target / "Dockerfile").write_text(dockerfile(spec), encoding="utf-8")

    if pack.get("model_init"):
        model_dir = dist / "model-init"
        model_dir.mkdir()
        (model_dir / "Dockerfile").write_text(MODEL_INIT_DOCKERFILE, encoding="utf-8")
        (model_dir / "requirements.txt").write_text(MODEL_INIT_REQUIREMENTS, encoding="utf-8")
        (model_dir / "download_models.py").write_text(MODEL_INIT_SCRIPT, encoding="utf-8")

    (dist / "compose.yaml").write_text(yaml.safe_dump(build_compose(pack_name, pack), sort_keys=False, allow_unicode=True), encoding="utf-8")
    env_lines = [
        "COMPOSE_PROJECT_NAME=yarsalam-" + pack_name,
        "REDIS_PASSWORD=CHANGE_ME",
        pack["admin_env"] + "=CHANGE_ME",
        "OPENAI_API_KEY=",
    ]
    (dist / ".env.example").write_text("\n".join(env_lines) + "\n", encoding="utf-8")
    (dist / "README.md").write_text(readme_for(pack_name, pack), encoding="utf-8")
    manifest = {
        "pack": pack_name, "label": pack["label"],
        "upstream_repository": "https://github.com/yarsalam/mobApp",
        "upstream_ref": str((__import__("subprocess").run(["git", "-C", str(upstream), "rev-parse", "HEAD"], capture_output=True, text=True).stdout or "unknown").strip()), "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "services": pack["services"], "gateway_port": pack["port"],
        "models_downloaded_at_install": bool(pack.get("model_init") or any("embedded_ai" in s for s in pack["services"])),
    }
    (dist / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["files"] = {
        str(p.relative_to(dist)): {"bytes": p.stat().st_size, "sha256": sha256_file(p)}
        for p in sorted(dist.rglob("*")) if p.is_file() and p.name != "manifest.json"
    }
    (dist / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.make_archive(str(output / pack_name), "zip", root_dir=dist)
    shutil.make_archive(str(output / (plugin_slug + "-wordpress")), "zip", root_dir=dist / "wordpress-plugin", base_dir=plugin_slug)
    return dist

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mobapp-root", type=Path, required=True, help="Path to a checkout of yarsalam/mobApp")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    upstream = args.mobapp_root.resolve()
    if not (upstream / "python-ai" / "services").is_dir():
        raise SystemExit(f"Not a mobApp checkout: {upstream}")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    built = []
    for pack_name, pack in PACKS.items():
        build_one(pack_name, pack, upstream, output)
        built.append(pack_name)
    index = {
        "upstream_repository": "https://github.com/yarsalam/mobApp", "packs": built,
        "artifacts": [f"{name}.zip" for name in built],
        "wordpress_plugins": [pack["plugin"][1] + "-wordpress.zip" for pack in PACKS.values()],
    }
    (output / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "packs": built}, indent=2))

if __name__ == "__main__":
    main()
