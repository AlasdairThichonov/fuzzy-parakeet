from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from deploy_guard.llm.providers import get_provider
from deploy_guard.llm.redaction import redact_text
from deploy_guard.models import ScanContext
from deploy_guard.reporting.json_report import build_report
from deploy_guard.reporting.markdown_report import build_markdown
from deploy_guard.rules.core_rules import build_registry
from deploy_guard.rules.engine import score_from_findings
from deploy_guard.scanners.detector import detect_project_types
from deploy_guard.scanners.helm import load_helm_chart
from deploy_guard.scanners.k8s import load_k8s_yaml
from deploy_guard.scanners.terraform import load_terraform

SEV_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def scan_path(path: str, threshold: int = 70, llm_enabled: bool = True, llm_provider: str = "dummy") -> tuple[dict[str, Any], str]:
    start = time.time()
    p = Path(path)
    types = detect_project_types(p)
    docs: list[dict[str, Any]] = []
    tf_blocks: list[dict[str, Any]] = []
    if "k8s" in types:
        docs.extend(load_k8s_yaml(p))
    if "helm" in types:
        docs.extend(load_helm_chart(p))
    if "terraform" in types:
        tf_blocks.extend(load_terraform(p))

    ctx = ScanContext(path=path, types_detected=types, docs=docs, tf_blocks=tf_blocks)
    registry = build_registry()
    findings = registry.run(ctx)
    score_data = score_from_findings(findings)

    report: dict[str, Any] = build_report(
        {
            "metadata": {"scanned_paths": [path], "types_detected": types},
            "summary": {
                "score": score_data["score"],
                "threshold": threshold,
                "pass": score_data["score"] < threshold,
                "duration_ms": int((time.time() - start) * 1000),
            },
            "breakdown": score_data["by_category"],
            "findings": [{**asdict(f), "severity": f.severity.value} for f in findings],
            "redaction": {"enabled": llm_enabled, "replacements_count": 0},
            "llm": {"enabled": llm_enabled, "provider": llm_provider, "summary_text": "", "mitigations": []},
        }
    )

    md = build_markdown(report)
    if llm_enabled:
        redacted, count = redact_text(json.dumps(report))
        provider = get_provider(llm_provider)
        summary, mitigations = provider.summarize(
            "Summarize deployment risk and provide mitigations:\n" + redacted
        )
        report["redaction"]["replacements_count"] = count
        report["llm"]["summary_text"] = summary
        report["llm"]["mitigations"] = mitigations
        md = build_markdown(report)
    return report, md


def should_fail(report: dict[str, Any], fail_on: str) -> bool:
    if report["summary"]["score"] >= int(report["summary"]["threshold"]):
        return True
    lvl = SEV_ORDER[fail_on]
    for f in report["findings"]:
        if SEV_ORDER[str(f["severity"])] >= lvl:
            return True
    return False
