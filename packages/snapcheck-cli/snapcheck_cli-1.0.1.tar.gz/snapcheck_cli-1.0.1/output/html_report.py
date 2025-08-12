import os
import shutil
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

SEV_BUCKET_ORDER = {"INFO": 0, "PASS": 1, "WARN": 2, "FAIL": 3}

def _bucket_status(raw):
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

def _coerce_items(plugin_name, obj):
    """Turn AuditResult or list[AuditResult/str] into a list of dicts."""
    items = []
    seq = obj if isinstance(obj, (list, tuple)) else [obj]
    for r in seq:
        if r is None:
            continue
        title = plugin_name.replace("_", " ").title()
        severity, message, meta = "INFO", "", None
        if hasattr(r, "messages"):
            msgs = getattr(r, "messages") or []
            if isinstance(msgs, str):
                msgs = [msgs]
            message = "\n".join(msgs)
            raw_status = getattr(getattr(r, "status", None), "value", getattr(r, "status", None))
            severity = _bucket_status(raw_status)
            if hasattr(r, "title") and getattr(r, "title"):
                title = getattr(r, "title")
            if hasattr(r, "metadata"):
                meta = getattr(r, "metadata")
        else:
            message = str(r)
            severity = "INFO"
        items.append({"title": title, "severity": severity, "message": message, "meta": meta})
    return items

def _aggregate_status(items):
    agg = "INFO"
    for it in items:
        s = _bucket_status(it.get("severity"))
        if SEV_BUCKET_ORDER[s] > SEV_BUCKET_ORDER[agg]:
            agg = s
    return agg

def _format_results(plugin_results):
    formatted = {}
    for name, val in (plugin_results or {}).items():
        items = _coerce_items(name, val)
        formatted[name] = {
            "title": name.replace("_", " ").title(),
            "status": _aggregate_status(items),
            "items": items,
            "stats": [],
        }
    return formatted

def _safe_charts(charts):
    return charts if isinstance(charts, dict) else {}

def _compute_cost_total(charts_dict):
    try:
        ds = charts_dict.get("cost", {}).get("datasets", [])
        if ds and isinstance(ds, list):
            data = ds[0].get("data", [])
            if isinstance(data, list):
                return sum(x for x in data if isinstance(x, (int, float)))
    except Exception:
        pass
    return 0

def _copy_static(out_dir: Path):
    """
    Copy output/static -> <report_dir>/static using an ABSOLUTE src path based on this file.
    Works regardless of current working directory (file://, local servers, Pages).
    """
    try:
        src = Path(__file__).resolve().parent / "static"
        dst = out_dir / "static"
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    except Exception:
        # Don't fail the report if assets can't be copied
        pass

def generate_html_report(plugin_results, summary=None, charts=None, gpt_summary="", diff=None, timestamp="", out_path=".snapcheck/report.html"):
    out_path = Path(out_path)
    os.makedirs(out_path.parent, exist_ok=True)

    # Absolute template path so this works no matter where CLI is invoked
    templates_dir = (Path(__file__).resolve().parent / "templates")
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("report_template.html")

    formatted_results = _format_results(plugin_results or {})
    charts_dict = _safe_charts(charts)
    summary = summary if isinstance(summary, dict) else {}
    diff = diff if isinstance(diff, dict) else {}
    gpt_summary = gpt_summary or ""

    # Defaults
    summary.setdefault("pass", 0)
    summary.setdefault("fail", 0)
    summary.setdefault("regressions", 0)
    summary.setdefault("cost_total", _compute_cost_total(charts_dict))

    kpis = [
        {"key": "pass", "label": "Passed Checks", "value": summary.get("pass", 0), "scroll_to": "kubernetes"},
        {"key": "fail", "label": "Failed Checks", "value": summary.get("fail", 0), "scroll_to": "terraform"},
        {"key": "regressions", "label": "Regressions", "value": summary.get("regressions", 0), "scroll_to": "correlation"},
        {"key": "cost", "label": "Monthly Cost", "value": f"${summary.get('cost_total', 0)}", "scroll_to": "cost"},
        {"key": "drift", "label": "Drifted Items", "value": len(diff.get("regressions", [])) if diff else 0, "scroll_to": "correlation"},
        {"key": "deploy", "label": "Last Deploy", "value": "—", "scroll_to": "ci_cd"},
    ]

    # Expose branding both in summary and top-level to match any template usage
    brand_title = summary.get("brand_title")
    brand_logo_url = summary.get("brand_logo_url")
    brand_subtitle = summary.get("brand_subtitle")
    brand_link = summary.get("brand_link")

    context = {
        "plugin_results": formatted_results,
        "summary": summary,
        "charts": charts_dict,
        "kpis": kpis,
        "gpt_summary": gpt_summary,
        "diff": diff,
        "timestamp": timestamp,
        # top-level branding (in case template uses {{ brand_* }})
        "brand_title": brand_title,
        "brand_logo_url": brand_logo_url,
        "brand_subtitle": brand_subtitle,
        "brand_link": brand_link,
    }

    # (Optional for one-run debugging)
    # rendered = f"<!-- tpl:{getattr(template, 'filename', '')} -->\n" + template.render(**context)
    rendered = template.render(**context)

    out_path.write_text(rendered, encoding="utf-8")

    # Ensure static assets are present next to the report (absolute source)
    _copy_static(out_path.parent)

    # Write history copy
    date_str = datetime.now().strftime("%Y-%m-%d")
    history_path = out_path.parent / f"report-{date_str}.html"
    history_path.write_text(rendered, encoding="utf-8")

    return str(out_path)