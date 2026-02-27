from __future__ import annotations

from pathlib import Path
from typing import Any


def _fallback_parse(text: str) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for chunk in text.split("---"):
        kind = ""
        name = ""
        for line in chunk.splitlines():
            s = line.strip()
            if s.startswith("kind:"):
                kind = s.split(":", 1)[1].strip()
            if s.startswith("name:") and not name:
                name = s.split(":", 1)[1].strip()
        if kind:
            docs.append({"kind": kind, "metadata": {"name": name}})
    return docs


def load_k8s_yaml(path: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    files = list(path.rglob("*.yaml")) + list(path.rglob("*.yml"))
    for f in files:
        if "templates" in f.parts and (path / "Chart.yaml").exists():
            continue
        text = f.read_text(encoding="utf-8")
        parsed: list[dict[str, Any]] = []
        try:
            import yaml  # type: ignore

            content = yaml.safe_load_all(text)
            for doc in content:
                if isinstance(doc, dict) and doc.get("kind"):
                    parsed.append(doc)
        except Exception:
            parsed = _fallback_parse(text)
        for doc in parsed:
            doc["__file"] = str(f)
            docs.append(doc)
    return docs
