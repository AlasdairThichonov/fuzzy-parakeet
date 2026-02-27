from deploy_guard.llm.redaction import redact_text


def test_redacts_sensitive_material() -> None:
    text = "password=abc123 token: zzz AKIAABCDEFGHIJKLMNOP"
    redacted, cnt = redact_text(text)
    assert "abc123" not in redacted
    assert "AKIAABCDEFGHIJKLMNOP" not in redacted
    assert cnt >= 2
