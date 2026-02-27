from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from datetime import UTC
except ImportError:  # pragma: no cover
    from datetime import timezone

    UTC = timezone.utc


def build_report(payload: dict[str, Any]) -> dict[str, Any]:
    payload["metadata"]["version"] = "0.1"
    payload["metadata"]["timestamp"] = datetime.now(tz=UTC).isoformat()
    return payload


def write_json(report: dict[str, Any], output: Path | None) -> str:
    text = json.dumps(report, indent=2)
    if output:
        output.write_text(text, encoding="utf-8")
    return text
