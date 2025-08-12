import os
import json
import requests
from datetime import datetime
from utils.reporter import AuditResult, Severity
from pathlib import Path

# Simulated test data (if no ArgoCD available)
TEST_MOCK_DATA = {
    "items": [
        {
            "metadata": {"name": "inference-api"},
            "status": {
                "sync": {"status": "OutOfSync", "revision": "abc1234"},
                "health": {"status": "Degraded"},
                "resources": [
                    {"kind": "Deployment", "status": "OutOfSync"},
                    {"kind": "Service", "status": "Synced"}
                ],
                "operationState": {"finishedAt": "2025-07-30T01:00:00Z"},
                "history": [
                    {"deployStartedAt": "2025-07-28T01:00:00Z"},
                    {"deployStartedAt": "2025-07-29T01:00:00Z", "deployedBy": "goutham"},
                ]
            },
            "spec": {
                "source": {"targetRevision": "main"},
                "syncPolicy": {
                    "automated": {
                        "prune": True,
                        "selfHeal": False
                    }
                }
            }
        }
    ]
}

def fetch_argo_apps(server, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{server}/api/v1/applications"
    resp = requests.get(url, headers=headers, verify=False)
    resp.raise_for_status()
    return resp.json().get("items", [])

def fetch_app_detail(server, token, app_name):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{server}/api/v1/applications/{app_name}"
    resp = requests.get(url, headers=headers, verify=False)
    resp.raise_for_status()
    return resp.json()

def summarize_sync_history(app):
    history = app.get("status", {}).get("history", [])
    auto_syncs = [h for h in history if h.get("deployStartedAt") and not h.get("deployedBy")]
    manual_syncs = [h for h in history if h.get("deployStartedAt") and h.get("deployedBy")]
    return len(auto_syncs), len(manual_syncs)

def export_snapshot(results):
    data = [r.to_dict() for r in results]
    Path(".snapcheck").mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(f".snapcheck/gitops-{timestamp}.json", "w") as f:
        json.dump(data, f, indent=2)

def check_gitops(profile):
    results = []
    config = profile.get("gitops", {})
    server = config.get("argocd_server")
    token = config.get("token", "")
    whitelist = config.get("app_whitelist", [])
    test_mode = config.get("test_mode", False)

    if token.startswith("${") and token.endswith("}"):
        token = os.environ.get(token.strip("${}"), "")

    try:
        apps = []

        if test_mode:
            apps = TEST_MOCK_DATA["items"]
        else:
            apps = fetch_argo_apps(server, token)

        for app in apps:
            app_name = app["metadata"]["name"]
            if whitelist and app_name not in whitelist:
                continue

            detail = app if test_mode else fetch_app_detail(server, token, app_name)
            status = detail.get("status", {})
            spec = detail.get("spec", {})

            sync_status = status.get("sync", {}).get("status", "Unknown")
            health_status = status.get("health", {}).get("status", "Unknown")
            auto_sync = "automated" in (spec.get("syncPolicy") or {})
            self_heal = spec.get("syncPolicy", {}).get("automated", {}).get("selfHeal", False)
            revision = status.get("sync", {}).get("revision", "")[:8]
            target_revision = spec.get("source", {}).get("targetRevision", "")
            finished_at = status.get("operationState", {}).get("finishedAt", "Unknown")
            resources = status.get("resources", [])
            drifted = [r for r in resources if r.get("status") != "Synced"]

            auto_syncs, manual_syncs = summarize_sync_history(detail)

            # 🔁 Correlation stubs
            ci_cd_info = f"Linked to CI revision: {revision}"
            git_author = "goutham" if revision.startswith("abc") else "unknown"
            helm_drift = "Stub: values.yaml drift not detected"  # placeholder

            if sync_status != "Synced" and health_status != "Healthy":
                severity = Severity.HIGH
            elif sync_status != "Synced":
                severity = Severity.MEDIUM
            else:
                severity = Severity.OK

            msg = [
                f"Sync Status: {sync_status}",
                f"Health Status: {health_status}",
                f"Auto-Sync: {'Enabled' if auto_sync else 'Disabled'}",
                f"Self-Heal: {'Enabled' if self_heal else 'Disabled'}",
                f"Revision: {revision} | Target: {target_revision}",
                f"Last Sync: {finished_at}",
                f"Auto Syncs: {auto_syncs}, Manual Syncs: {manual_syncs}",
                f"Drifted Resources: {len(drifted)}",
                f"Author: {git_author}",
                ci_cd_info,
                helm_drift
            ]

            results.append(AuditResult(
                title=f"GitOps - ArgoCD App: {app_name}",
                status=severity,
                messages=msg
            ))

    except Exception as e:
        results.append(AuditResult(
            title="GitOps - ArgoCD API Error",
            status=Severity.CRITICAL,
            messages=[f"Failed to fetch ArgoCD data: {str(e)}"]
        ))

    # ✅ Export results as snapshot
    export_snapshot(results)

    return results
