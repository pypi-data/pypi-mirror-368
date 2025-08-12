import os
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Tuple

from utils.sanitize import deep_mask

SEV_BUCKET_ORDER = {"INFO": 0, "PASS": 1, "WARN": 2, "FAIL": 3}
SEV_EMOJI = {"INFO": "ℹ️", "PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}


def _bucket_status(raw: Any) -> str:
    if raw is None:
        return "INFO"
    u = str(raw).upper()
    if u in ("PASS", "OK", "SUCCESS"):
        return "PASS"
    if u in ("WARN", "WARNING", "MEDIUM", "LOW"):
        return "WARN"
    if u in ("FAIL", "HIGH", "CRITICAL", "ERROR", "SEVERE"):
        return "FAIL"
    if u in ("INFO", "UNKNOWN"):
        return "INFO"
    return "INFO"


def _coerce_items(plugin_name: str, obj: Any) -> List[Dict[str, Any]]:
    """
    Turn AuditResult or list[AuditResult/str] into a list of dicts:
    [{ title, severity, message, meta }]
    """
    items: List[Dict[str, Any]] = []
    seq = obj if isinstance(obj, (list, tuple)) else [obj]
    for r in seq:
        if r is None:
            continue
        title = plugin_name.replace("_", " ").title()
        severity, message, meta = "INFO", "", None

        # AuditResult-like
        if hasattr(r, "messages"):
            msgs = getattr(r, "messages") or []
            if isinstance(msgs, str):
                msgs = [msgs]
            message = "\n".join(str(m) for m in msgs)
            raw_status = getattr(getattr(r, "status", None), "value", getattr(r, "status", None))
            severity = _bucket_status(raw_status)
            if hasattr(r, "title") and getattr(r, "title"):
                title = getattr(r, "title")
            if hasattr(r, "metadata"):
                meta = getattr(r, "metadata")
        else:
            # plain string or unknown
            message = str(r)
            severity = "INFO"

        items.append({"title": title, "severity": severity, "message": message, "meta": meta})
    return items


def _aggregate_status(items: List[Dict[str, Any]]) -> str:
    agg = "INFO"
    for it in items:
        s = _bucket_status(it.get("severity"))
        if SEV_BUCKET_ORDER[s] > SEV_BUCKET_ORDER[agg]:
            agg = s
    return agg


def _format_module_header(name: str, status: str) -> str:
    emoji = SEV_EMOJI.get(status, "ℹ️")
    title = name.replace("_", " ").title()
    return f"### {title} — {emoji} {status}"


def _format_item_line(item: Dict[str, Any]) -> List[str]:
    sev = _bucket_status(item.get("severity"))
    emoji = SEV_EMOJI.get(sev, "ℹ️")
    title = item.get("title") or "Item"
    msg = item.get("message") or ""
    lines = [f"- **[{sev}]** {emoji} **{title}**"]
    if msg.strip():
        # indent as code block for readability
        lines.append("  ```")
        # keep message intact; masking is applied before rendering
        lines.extend([f"  {line}" for line in msg.splitlines()])
        lines.append("  ```")
    return lines


def _format_modules_table(formatted: Dict[str, Dict[str, Any]]) -> List[str]:
    lines = [
        "| Module | Status |",
        "|---|---|",
    ]
    for name, data in formatted.items():
        status = data.get("status", "INFO")
        emoji = SEV_EMOJI.get(status, "ℹ️")
        lines.append(f"| {name} | {emoji} {status} |")
    lines.append("")  # blank line
    return lines


def save_markdown_report(profile_name: str, results: Dict[str, Any]) -> str:
    """
    Generate a masked, readable Markdown report.

    Writes:
      - .snapcheck/report.md (latest)
      - .snapcheck/report-YYYY-MM-DD.md (history)
      - audit_YYYY-MM-DD_<profile>.md (legacy filename for compatibility)

    Returns the path to .snapcheck/report.md
    """
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    date_only = now.strftime("%Y-%m-%d")

    profile_base = os.path.basename(profile_name).split(".")[0]

    # Normalize + structure results similar to HTML path
    formatted: Dict[str, Dict[str, Any]] = {}
    for name, val in (results or {}).items():
        items = _coerce_items(name, val)
        formatted[name] = {
            "title": name.replace("_", " ").title(),
            "status": _aggregate_status(items),
            "items": items,
            "stats": [],
        }

    # Build markdown sections
    lines: List[str] = []
    lines.append(f"# SnapCheck Audit Report — {profile_base}")
    lines.append(f"_Audit Timestamp: {timestamp}_")
    lines.append("")

    # Module summary table
    lines.append("## Modules Summary")
    lines.extend(_format_modules_table(formatted))

    # Per-module details
    lines.append("## Module Details")
    for name, data in formatted.items():
        lines.append(_format_module_header(name, data.get("status", "INFO")))
        lines.append("")
        items = data.get("items", [])
        if not items:
            lines.append("_No findings._")
            lines.append("")
            continue
        for it in items:
            lines.extend(_format_item_line(it))
        lines.append("")

    # Apply universal masking to the final text (belt-and-suspenders),
    # and also to any dict-like data used above (already safe by construction).
    md_text = "\n".join(lines)
    md_text = deep_mask(md_text)  # final scrub

    # Ensure output dirs
    out_dir = Path(".snapcheck")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Latest and history file paths
    latest_path = out_dir / "report.md"
    history_path = out_dir / f"report-{date_only}.md"

    # Legacy filename for backward compatibility with your original function
    legacy_filename = f"audit_{date_only}_{profile_base}.md"
    legacy_path = Path(legacy_filename)

    # Write files
    latest_path.write_text(md_text, encoding="utf-8")
    history_path.write_text(md_text, encoding="utf-8")
    legacy_path.write_text(md_text, encoding="utf-8")

    return str(latest_path)
