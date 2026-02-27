from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any

from deploy_guard.models import Finding, RuleMeta, ScanContext

RuleFunc = Callable[[ScanContext], list[Finding]]


class RuleRegistry:
    def __init__(self) -> None:
        self._rules: list[tuple[RuleMeta, RuleFunc]] = []

    def register(self, meta: RuleMeta, func: RuleFunc) -> None:
        self._rules.append((meta, func))

    def list_rules(self) -> list[RuleMeta]:
        return [m for m, _ in self._rules]

    def run(self, ctx: ScanContext) -> list[Finding]:
        findings: list[Finding] = []
        for _, func in self._rules:
            findings.extend(func(ctx))
        return findings


def score_from_findings(findings: list[Finding]) -> dict[str, Any]:
    total_impact = sum(f.score_impact for f in findings)
    score = min(100, total_impact)
    by_category: dict[str, int] = defaultdict(int)
    for f in findings:
        by_category[f.category] += f.score_impact
    return {"score": score, "by_category": dict(by_category)}
