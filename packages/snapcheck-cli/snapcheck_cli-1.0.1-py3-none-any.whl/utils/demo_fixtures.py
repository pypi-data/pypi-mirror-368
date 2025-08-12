# utils/demo_fixtures.py
from datetime import datetime
from typing import Dict, Any, List, Optional
from utils.reporter import AuditResult, Severity

# --- dynamic severity adapters ----------------------------------------------

def _members() -> List[Severity]:
    try:
        return list(Severity)  # Enum is iterable
    except Exception:
        # extremely defensive: grab attributes that look like Enum members
        return [v for k, v in Severity.__dict__.items() if getattr(v, "__class__", None).__name__ == "Severity"]

def _find_member(prefer: List[str]) -> Optional[Severity]:
    if not prefer:
        return None
    prefer_u = [p.upper() for p in prefer]
    for m in _members():
        name_u = getattr(m, "name", "").upper()
        val_u = str(getattr(m, "value", "")).upper()
        if any(p == name_u or p == val_u for p in prefer_u):
            return m
        if any(p in name_u or p in val_u for p in prefer_u):
            return m
    return None

def S(level: str) -> Severity:
    """
    Map abstract levels ('pass','warn','info','fail') to *existing* enum members.
    Falls back to:
      - something 'LOW/OK/INFO' for pass/info
      - something 'WARN/MEDIUM' for warn
      - something 'FAIL/HIGH/CRITICAL/ERROR' for fail
      - otherwise: the first member in the enum
    """
    lvl = (level or "").lower()

    if lvl in ("pass", "ok", "success", "low", "info"):
        m = _find_member(["PASS","OK","SUCCESS","LOW","INFO"])
        if m: return m
    if lvl in ("warn", "warning", "medium"):
        m = _find_member(["WARN","WARNING","MEDIUM"])
        if m: return m
    if lvl in ("fail", "failure", "high", "critical", "error", "severe"):
        m = _find_member(["FAIL","FAILURE","HIGH","CRITICAL","ERROR","SEVERE"])
        if m: return m
    if lvl in ("info",):
        m = _find_member(["INFO","LOW","OK","SUCCESS"])
        if m: return m

    # final fallback: first enum member
    try:
        return list(Severity)[0]
    except Exception:
        # as an absolute last resort, try attribute lookup heuristics
        for cand in ("LOW","INFO","WARN","WARNING","FAIL","CRITICAL","ERROR","UNKNOWN"):
            m = _find_member([cand])
            if m: return m
        raise RuntimeError("Could not resolve any Severity enum member for demo fixtures.")

# --- helpers -----------------------------------------------------------------

def _ar(title: str, status: str, msgs: List[str], meta: Optional[dict] = None) -> AuditResult:
    r = AuditResult(title=title, status=S(status), messages=msgs)
    if meta:
        try:
            # some implementations have .metadata attribute; if not, ignore
            r.metadata = meta
        except Exception:
            pass
    return r

# --- public API --------------------------------------------------------------

def get_demo_results(config: Dict[str, Any]) -> Dict[str, Any]:
    # Realistic-but-static demo outputs (no external calls)
    return {
        "terraform": _ar(
            "Terraform",
            "pass",
            ["No drift detected in last snapshot.", "State age: 2 days."]
        ),
        "kubernetes": _ar(
            "Kubernetes",
            "warn",
            [
                "2 pods restarting (CrashLoopBackOff) in monitoring namespace.",
                "Node pressure: none. DNS: OK."
            ]
        ),
        "helm": _ar(
            "Helm",
            "pass",
            ["All releases healthy. 1 chart outdated (minor)."],
            meta={"outdated": [{"name": "prometheus", "current": "19.6.0", "latest": "19.7.1"}]}
        ),
        "ci_cd": _ar(
            "CI/CD",
            "info",
            [
                "Avg durations — Build: 22s, Test: 41s, Deploy: 19s.",
                "Branch protection: enabled on main."
            ]
        ),
        "docker": _ar(
            "Docker",
            "info",
            ["2 images scanned via registry API. No critical CVEs.", "Largest image: 412 MB."]
        ),
        "secrets": _ar(
            "Secrets",
            "info",
            ["No high-risk hardcoded secrets detected in tracked paths.", "Kubernetes secrets: 12 (10 used, 2 unused)."]
        ),
        "cost": _ar(
            "Cost",
            "info",
            ["Monthly AWS cost (last 4 months): $120 → $150 → $90 → $170."],
            meta={"monthly_cost_usd": [120, 150, 90, 170]}
        ),
        "gitops": _ar(
            "GitOps",
            "pass",
            ["ArgoCD apps in sync ✅  Self-heal: enabled."]
        ),
        "correlation": _ar(
            "Root Cause Correlation",
            "info",
            ["Potential link: image size growth ↔ longer build times.", "No incident linkage detected in last 24h."]
        ),
    }

def get_demo_summary_and_charts(results: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    # Simple computed summary from whatever your Severity enum is
    statuses = []
    for v in results.values():
        s = getattr(getattr(v, "status", None), "name", "") or str(getattr(v, "status", ""))
        statuses.append(s.upper())

    # Be generous in what we accept for pass/fail buckets
    passed = sum(1 for s in statuses if any(k in s for k in ("PASS", "OK", "SUCCESS", "LOW")))
    failed = sum(1 for s in statuses if any(k in s for k in ("FAIL", "FAILURE", "CRITICAL", "ERROR", "SEVERE", "HIGH")))

    summary = {
        "pass": passed,
        "fail": failed,
        "regressions": 0,
        "cost_total": 120 + 150 + 90 + 170,
        "demo_mode": True,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    charts = {
        "cost": {
            "labels": ["Jan", "Feb", "Mar", "Apr"],
            "datasets": [{
                "label": "AWS Cost ($)",
                "data": [120, 150, 90, 170],
                "fill": False,
                "borderColor": "rgb(75, 192, 192)",
                "tension": 0.1
            }]
        },
        "ci": {
            "labels": ["Build", "Test", "Deploy"],
            "datasets": [{
                "label": "Avg Duration (s)",
                "data": [22, 41, 19],
            }]
        }
    }
    return summary, charts

    return summary, charts