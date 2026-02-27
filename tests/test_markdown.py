from deploy_guard.reporting.markdown_report import build_markdown


def test_markdown_renders_sections() -> None:
    report = {
        "summary": {"score": 80, "threshold": 70, "pass": False},
        "breakdown": {"Kubernetes Security": 30},
        "findings": [{"rule_id": "X", "severity": "high", "message": "bad", "file": "a.yaml", "references": ["http://x"]}],
        "llm": {"mitigations": ["do thing"]},
    }
    md = build_markdown(report)
    assert "Deploy Guard Report" in md
    assert "Top Findings" in md
    assert "Mitigation Checklist" in md
