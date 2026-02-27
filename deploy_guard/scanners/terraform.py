from __future__ import annotations

from pathlib import Path
from typing import Any


def load_terraform(path: Path) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for f in path.rglob("*.tf"):
        if ".terraform" in f.parts:
            continue
        text = f.read_text(encoding="utf-8")
        parsed: dict[str, Any] = {"__file": str(f), "raw": text}
        try:
            import hcl2

            with f.open("r", encoding="utf-8") as stream:
                parsed = hcl2.load(stream)
            parsed["__file"] = str(f)
        except Exception:
            pass
        blocks.append(parsed)
    return blocks
