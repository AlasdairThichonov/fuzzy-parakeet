from __future__ import annotations

import re

PATTERNS = [
    re.compile(r"(?i)(password|secret|token|apikey|api_key|private_key|client_secret|access_key)\s*[:=]\s*['\"]?([^\s'\"]+)") ,
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)bearer\s+[a-z0-9\-\._~\+/]+=*"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
]


def redact_text(text: str) -> tuple[str, int]:
    replaced = 0
    out = text
    for p in PATTERNS:
        out, count = p.subn("[REDACTED]", out)
        replaced += count
    return out, replaced
