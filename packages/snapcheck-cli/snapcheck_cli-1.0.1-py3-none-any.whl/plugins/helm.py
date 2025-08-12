import subprocess
import yaml
import os
from utils.reporter import AuditResult, Severity


def get_helm_releases(namespaces):
    releases = []
    for ns in namespaces:
        try:
            cmd = ["helm", "list", "-n", ns, "-o", "yaml"]
            output = subprocess.check_output(cmd, text=True)
            data = yaml.safe_load(output)
            for release in data:
                release["namespace"] = ns
                releases.append(release)
        except subprocess.CalledProcessError:
            continue
    return releases


def compare_values_vs_live(name, ns):
    try:
        live_values = subprocess.check_output([
            "helm", "get", "values", name, "-n", ns, "--output", "yaml"
        ], text=True)
        if os.path.exists(f"helm/{name}/values.yaml"):
            with open(f"helm/{name}/values.yaml", "r") as f:
                local_values = f.read()
            return live_values.strip() != local_values.strip()
        return False
    except Exception:
        return False


def check_outdated_charts():
    try:
        subprocess.run(["helm", "repo", "update"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outdated = subprocess.check_output([
            "helm", "list", "--all-namespaces", "--outdated", "-o", "yaml"
        ], text=True)
        return yaml.safe_load(outdated)
    except Exception:
        return []


def run_check(config):
    test_mode = config.get("test_mode", False)
    namespaces = config.get("helm_namespaces", ["default"])

    if test_mode:
        return AuditResult(
            title="Helm Audit",
            status=Severity.OK,
            messages=["Test mode enabled. Skipping Helm diagnostics."]
        )

    try:
        subprocess.check_output(["helm", "version"], stderr=subprocess.DEVNULL)
    except Exception as e:
        return AuditResult(
            title="Helm Audit",
            status=Severity.CRITICAL,
            messages=[f"❌ Helm not installed or not working: {e}"]
        )

    messages = []
    severity = Severity.OK
    releases = get_helm_releases(namespaces)
    outdated = check_outdated_charts()
    outdated_names = [r["name"] for r in outdated if isinstance(r, dict)]

    failed = []
    drifted = []

    for release in releases:
        name = release.get("name")
        ns = release.get("namespace")
        if release.get("status") != "deployed":
            failed.append(f"{name} in {ns} - status: {release.get('status')}")
        if compare_values_vs_live(name, ns):
            drifted.append(f"{name} in {ns}")

    if outdated_names:
        messages.append(f"📦 Outdated releases: {', '.join(outdated_names)}")
        severity = Severity.MEDIUM
    if failed:
        messages.append(f"❌ Failed releases: {', '.join(failed)}")
        severity = Severity.HIGH
    if drifted:
        messages.append(f"🔄 Drifted values.yaml: {', '.join(drifted)}")
        if severity == Severity.OK:
            severity = Severity.MEDIUM

    if not messages:
        messages.append("✅ All Helm releases are healthy and up-to-date.")

    return AuditResult(
        title="Helm Audit",
        status=severity,
        messages=messages
    )


