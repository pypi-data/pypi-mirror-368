import re
from typing import Any

# Precompiled patterns: common cloud/API keys, JWTs, PEM blocks, base64-ish blobs, long tokens, URL creds
_PATTERNS = [
    re.compile(r'AKIA[0-9A-Z]{16}'),                                   # AWS Access Key
    re.compile(r'ASIA[0-9A-Z]{16}'),                                   # AWS STS
    re.compile(r'(?i)\bghp_[0-9a-z]{20,}\b'),                          # GitHub classic
    re.compile(r'(?i)\bgithub_pat_[0-9a-z_]{20,}\b'),                  # GitHub fine-grained
    re.compile(r'(?i)\b(xox[aboprs]-[0-9A-Za-z-]{10,})\b'),            # Slack tokens
    re.compile(r'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'),  # JWT-ish
    re.compile(r'-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]+?-----END [A-Z ]+PRIVATE KEY-----'),
    re.compile(r'-----BEGIN OPENSSH PRIVATE KEY-----[\s\S]+?-----END OPENSSH PRIVATE KEY-----'),
    re.compile(r'(?i)(secret|token|password|passwd|pwd|api[_-]?key)\s*[:=]\s*([^\s,;]+)'),   # k=v or k: v
    re.compile(r'[A-Za-z0-9+/]{28,}={0,2}'),                            # base64-like long strings
    re.compile(r'\b[A-Za-z0-9._%+-]+:([^\s@]+)@'),                      # user:pass@ in URLs
    re.compile(r'\b(?:[A-Fa-f0-9]{32,}|[A-Za-z0-9_-]{40,})\b'),         # long hex/tokens
]

def _mask_str(s: str, replacement: str = "****") -> str:
    out = s
    for pat in _PATTERNS:
        out = pat.sub(replacement, out)
    return out

def deep_mask(obj: Any, replacement: str = "****") -> Any:
    if obj is None:
        return None
    if isinstance(obj, str):
        return _mask_str(obj, replacement)
    if isinstance(obj, dict):
        return {k: deep_mask(v, replacement) for k, v in obj.items()}
    if isinstance(obj, list):
        return [deep_mask(v, replacement) for v in obj]
    # For objects with __dict__/dataclass style
    if hasattr(obj, "__dict__"):
        d = {k: getattr(obj, k) for k in obj.__dict__.keys() if not k.startswith("_")}
        return deep_mask(d, replacement)
    return obj
