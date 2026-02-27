from pathlib import Path

from deploy_guard.scanners.detector import detect_project_types


def test_detect_mixed_demo() -> None:
    kinds = detect_project_types(Path("demo"))
    assert set(kinds) == {"k8s", "terraform"}
