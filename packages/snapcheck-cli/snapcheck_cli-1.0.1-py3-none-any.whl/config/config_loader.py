import sys
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import ValidationError

# Your schema (keep as-is)
from config.profile_schema import ProfileConfig


def load_config(profile_path: str) -> Dict[str, Any]:
    """
    Load YAML profile, validate known fields with ProfileConfig,
    and preserve any extra/unknown sections (e.g., `security`).

    Behavior:
      - YAML parse errors raise a readable exception (and return {}).
      - Pydantic validation is enforced for known fields.
      - Unknown keys are merged back so web/server.py can read them.

    Returns:
      Dict[str, Any] - final merged config
    """
    path = Path(profile_path)

    if not path.exists():
        print(f"[SnapCheck] ❌ Profile not found: {path.resolve()}", file=sys.stderr)
        return {}

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(raw, dict):
            print(f"[SnapCheck] ❌ Profile must be a mapping (dict). Got: {type(raw).__name__}", file=sys.stderr)
            return {}

    except Exception as e:
        print(f"[SnapCheck] ❌ YAML parse error for {path.resolve()}: {e}", file=sys.stderr)
        return {}

    # Validate known fields strictly
    try:
        validated = ProfileConfig(**raw)
    except ValidationError as e:
        # Keep the error loud so callers see the real issue
        print(f"[SnapCheck] ❌ Schema Validation Error in {path.resolve()}:\n{e}", file=sys.stderr)
        raise

    # Merge: validated (normalized) values win; unknown keys are preserved from raw
    cfg: Dict[str, Any] = {**raw, **validated.dict()}

    # Optional: sanity log
    # print(f"[SnapCheck] Loaded profile OK: {path.resolve()} | keys={list(cfg.keys())}")

    return cfg