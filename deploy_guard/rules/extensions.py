from __future__ import annotations

from importlib.metadata import entry_points


def discover_external_rules() -> list[str]:
    eps = entry_points(group="deploy_guard.rules")
    return [ep.name for ep in eps]
