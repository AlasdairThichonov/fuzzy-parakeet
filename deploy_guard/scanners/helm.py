from __future__ import annotations

from pathlib import Path
from typing import Any

from deploy_guard.scanners.k8s import _fallback_parse


def load_helm_chart(path: Path) -> list[dict[str, Any]]:
    templates = path / "templates"
    docs: list[dict[str, Any]] = []
    if not templates.exists():
        return docs
    for f in list(templates.rglob("*.yaml")) + list(templates.rglob("*.yml")):
        text = f.read_text(encoding="utf-8")
        if "{{" in text:
            continue
        parsed: list[dict[str, Any]] = []
        try:
            import yaml  # type: ignore

            for doc in yaml.safe_load_all(text):
                if isinstance(doc, dict) and doc.get("kind"):
                    parsed.append(doc)
        except Exception:
            parsed = _fallback_parse(text)
        for doc in parsed:
            doc["__file"] = str(f)
            docs.append(doc)
    return docs
