from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class Finding:
    rule_id: str
    title: str
    severity: Severity
    category: str
    score_impact: int
    description: str
    remediation: str
    references: list[str]
    file: str
    line: int | None
    resource: str
    message: str


@dataclass(slots=True)
class RuleMeta:
    id: str
    title: str
    severity: Severity
    category: str
    score_impact: int
    description: str
    remediation: str
    references: list[str]


@dataclass(slots=True)
class ScanContext:
    path: str
    types_detected: list[str]
    docs: list[dict[str, Any]] = field(default_factory=list)
    tf_blocks: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class ScanResult:
    findings: list[Finding]
    metadata: dict[str, Any]
