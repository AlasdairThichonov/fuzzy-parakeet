from __future__ import annotations

from pathlib import Path


def detect_project_types(path: Path) -> list[str]:
    kinds: set[str] = set()
    if (path / "Chart.yaml").exists() and (path / "templates").exists():
        kinds.add("helm")

    for f in path.rglob("*.tf"):
        if ".terraform" not in f.parts:
            kinds.add("terraform")
            break

    for f in list(path.rglob("*.yaml")) + list(path.rglob("*.yml")):
        if "templates" in f.parts and (path / "Chart.yaml").exists():
            continue
        kinds.add("k8s")
        break

    return sorted(kinds)
