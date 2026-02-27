from deploy_guard.service import scan_path


def test_scoring_has_range() -> None:
    report, _ = scan_path("demo", llm_enabled=False)
    assert 0 <= report["summary"]["score"] <= 100
    assert isinstance(report["breakdown"], dict)
