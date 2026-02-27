from __future__ import annotations

from typing import Any


def build_markdown(report: dict[str, Any]) -> str:
    s = report["summary"]
    lines = [
        "# Deploy Guard Report",
        f"**Score:** {s['score']}/100  ",
        f"**Threshold:** {s['threshold']}  ",
        f"**Deployment Readiness:** {'✅ PASS' if s['pass'] else '❌ FAIL'}",
        "",
        "## Breakdown",
        "| Category | Impact |",
        "|---|---:|",
    ]
    for k, v in report["breakdown"].items():
        lines.append(f"| {k} | {v} |")

    lines.append("\n## Top Findings")
    for f in report["findings"][:10]:
        lines.append(f"- **{f['rule_id']}** ({f['severity']}): {f['message']} — `{f['file']}`")

    lines.append("\n## Mitigation Checklist")
    for item in report.get("llm", {}).get("mitigations", []):
        lines.append(f"- [ ] {item}")

    refs: set[str] = set()
    for f in report["findings"]:
        refs.update(f.get("references", []))
    lines.append("\n## References")
    for r in sorted(refs):
        lines.append(f"- {r}")
    return "\n".join(lines)
