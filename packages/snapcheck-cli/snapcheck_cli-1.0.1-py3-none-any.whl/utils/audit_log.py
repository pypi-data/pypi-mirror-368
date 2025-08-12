import json, time
from pathlib import Path

def write_audit_event(kind: str, details: dict):
    try:
        out_dir = Path(".snapcheck")
        out_dir.mkdir(parents=True, exist_ok=True)
        line = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event": kind,
            **(details or {}),
        }
        with open(out_dir / "audit_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
    except Exception:
        pass
