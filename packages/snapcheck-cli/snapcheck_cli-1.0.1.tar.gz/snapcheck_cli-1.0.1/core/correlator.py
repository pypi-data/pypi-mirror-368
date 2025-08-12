import os
import json
import requests
import datetime
import socket
import ssl
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import boto3
from utils.reporter import AuditResult, Severity

# === MAIN CORRELATION ENGINE ===
def correlate(results):
    additional = []

    # --- Core Correlation ---
    core_result = correlate_root_cause(results)
    additional.append(core_result)

    # --- Infra Drift ---
    drift = detect_infra_drift(".snapcheck/terraform.tfstate")
    if drift:
        additional.append(drift)

    # --- Change Velocity ---
    change = summarize_change_velocity(results)
    if change:
        additional.append(change)

    # --- Snapshot Diff ---
    snapshot = detect_snapshot_drift()
    if snapshot:
        additional.append(snapshot)

    # --- Ownership Tags ---
    ownership = detect_ownership(results)
    if ownership:
        additional.append(ownership)

    # --- Incident Integration ---
    incidents = correlate_incidents()
    if incidents:
        additional.append(incidents)

    # --- Prometheus Rule Gaps ---
    alert_gap = analyze_alert_rules()
    if alert_gap:
        additional.append(alert_gap)

    # --- Endpoint Uptime ---
    uptime = check_endpoints()
    if uptime:
        additional.append(uptime)

    # --- Test Coverage ---
    coverage = summarize_test_coverage()
    if coverage:
        additional.append(coverage)

    # --- Cost Spike Anomaly ---
    cost_spike = detect_cost_spikes()
    if cost_spike:
        additional.append(cost_spike)

    return additional


# === CORE CORRELATION ===
def correlate_root_cause(results):
    if not isinstance(results.get("ci_cd"), list) or not isinstance(results.get("gitops"), list):
        return AuditResult("Root Cause Correlation", Severity.LOW, [
            "Correlation skipped due to missing or invalid CI/CD or GitOps results."
        ])

    ci_commits = extract_ci_commits(results.get("ci_cd", []))
    helm_tags = extract_helm_mappings(results.get("helm", []))
    gitops_state = extract_gitops_state(results.get("gitops", []))
    k8s_problems = extract_k8s_problems(results.get("kubernetes", []))

    correlations = []

    for sha in ci_commits:
        helm_tag_match = helm_tags.get(sha)
        if not helm_tag_match:
            continue

        gitops_match = gitops_state.get(sha)
        if not gitops_match:
            continue

        affected_k8s = k8s_problems.get(gitops_match.get("app"))

        message = f"🔗 Commit {sha} ➔ CI job ➔ Helm tag ➔ ArgoCD app {gitops_match.get('app')}"
        if affected_k8s:
            message += f" ➔ K8s issue: {affected_k8s}"

        correlations.append(message)

    severity = Severity.CRITICAL if correlations else Severity.OK
    messages = correlations or ["No linked root cause issues found."]

    os.makedirs(".snapcheck", exist_ok=True)
    with open(".snapcheck/correlations.json", "w") as f:
        json.dump(messages, f, indent=2)

    return AuditResult("Root Cause Correlation", severity, messages)


# === INFRA DRIFT ===
def detect_infra_drift(tfstate_path, aws_region="us-east-1"):
    local_tf_path = tfstate_path

    # === Handle remote HTTP/HTTPS .tfstate ===
    if tfstate_path.startswith("http://") or tfstate_path.startswith("https://"):
        try:
            r = requests.get(tfstate_path)
            r.raise_for_status()
            local_tf_path = ".snapcheck/terraform.tfstate"
            os.makedirs(".snapcheck", exist_ok=True)
            with open(local_tf_path, "w") as f:
                f.write(r.text)
        except Exception as e:
            return AuditResult("Infra Drift Detection", Severity.CRITICAL, [f"Failed to fetch remote tfstate: {e}"])

    # === Handle S3 .tfstate ===
    elif tfstate_path.startswith("s3://"):
        try:
            _, _, bucket_key = tfstate_path.partition("s3://")
            bucket, _, key = bucket_key.partition("/")
            s3 = boto3.client("s3", region_name=aws_region)
            obj = s3.get_object(Bucket=bucket, Key=key)
            content = obj['Body'].read().decode('utf-8')

            local_tf_path = ".snapcheck/terraform.tfstate"
            os.makedirs(".snapcheck", exist_ok=True)
            with open(local_tf_path, "w") as f:
                f.write(content)
        except Exception as e:
            return AuditResult("Infra Drift Detection", Severity.CRITICAL, [f"Failed to download S3 tfstate: {e}"])

    if not os.path.exists(local_tf_path):
        return AuditResult("Infra Drift Detection", Severity.CRITICAL, ["Terraform state file not found."])

    try:
        with open(local_tf_path) as f:
            tfstate = json.load(f)

        ec2 = boto3.client("ec2", region_name=aws_region)
        s3 = boto3.client("s3", region_name=aws_region)
        drifts = []

        expected_instances = set()
        actual_instances = set(i["InstanceId"] for r in ec2.describe_instances()["Reservations"] for i in r["Instances"])

        for res in tfstate["resources"]:
            if res["type"] == "aws_instance":
                for inst in res["instances"]:
                    instance_id = inst["attributes"].get("id")
                    if instance_id:
                        expected_instances.add(instance_id)

                        live = ec2.describe_instances(InstanceIds=[instance_id])
                        live_type = live["Reservations"][0]["Instances"][0]["InstanceType"]
                        tf_type = inst["attributes"].get("instance_type")
                        if tf_type != live_type:
                            drifts.append(f"EC2 {instance_id} ➔ instance_type drift: TF={tf_type}, Live={live_type}")

        missing = expected_instances - actual_instances
        extra = actual_instances - expected_instances

        for mid in missing:
            drifts.append(f"❌ EC2 {mid} in TF state but missing in AWS")
        for xid in extra:
            drifts.append(f"⚠️ EC2 {xid} in AWS but not managed by Terraform")

        tf_s3_buckets = [inst["attributes"]["bucket"] for r in tfstate["resources"] if r["type"] == "aws_s3_bucket" for inst in r["instances"]]
        live_s3_buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]

        for bucket in tf_s3_buckets:
            if bucket not in live_s3_buckets:
                drifts.append(f"❌ S3 bucket {bucket} in TF state but missing in AWS")

        if drifts:
            return AuditResult("Infra Drift Detection", Severity.HIGH, drifts)
        else:
            return AuditResult("Infra Drift Detection", Severity.OK, ["No drift detected"])

    except Exception as e:
        return AuditResult("Infra Drift Detection", Severity.CRITICAL, [f"Drift check error: {str(e)}"])


# === CHANGE VELOCITY ===
def summarize_change_velocity(results):
    ci_cd = results.get("ci_cd", [])
    if not isinstance(ci_cd, list):
        return None

    deploys = 0
    for r in ci_cd:
        if hasattr(r, "messages"):
            for msg in r.messages:
                if "avg_duration" in msg or "deploys" in msg:
                    deploys += 1

    return AuditResult("Change Velocity", Severity.OK, [f"Total recent deployments: {deploys}"])


# === SNAPSHOT DIFFING ===
def detect_snapshot_drift():
    current = ".snapcheck/ci_cd.json"
    prev = ".snapcheck/ci_cd_prev.json"
    if os.path.exists(current) and os.path.exists(prev):
        with open(current) as f1, open(prev) as f2:
            c1 = json.load(f1)
            c2 = json.load(f2)
            if c1 != c2:
                return AuditResult("Snapshot Drift", Severity.MEDIUM, ["Changes detected between last runs."])
    return None


# === OWNERSHIP DETECTION ===
def detect_ownership(results):
    owners = []
    for k, v in results.items():
        if isinstance(v, list):
            for r in v:
                if hasattr(r, "title") and "goutham" in r.title.lower():
                    owners.append(f"{r.title} ➔ Owner: goutham")
    if owners:
        return AuditResult("Ownership Mapping", Severity.OK, owners)
    return None


# === INCIDENT INTEGRATION ===
def correlate_incidents():
    path = ".snapcheck/incidents.json"
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        return AuditResult("Incident Linkage", Severity.HIGH, [f"Incident: {i}" for i in data.get("alerts", [])])
    return None


# === PROMETHEUS RULE GAPS ===
def analyze_alert_rules():
    rule_path = "prometheus/alert.rules"
    if os.path.exists(rule_path):
        with open(rule_path) as f:
            rules = f.read().lower()
            required = ["cpu", "memory", "disk", "pod", "kube"]
            missing = [r for r in required if r not in rules]
            if missing:
                return AuditResult("Alert Rule Gaps", Severity.MEDIUM, [f"Missing rules: {', '.join(missing)}"])
    return None


# === ENDPOINT UPTIME ===
def check_endpoints():
    urls = ["https://example.com", "https://grafana.example.com"]
    issues = []
    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                issues.append(f"{url} returned {r.status_code}")

            parsed = urlparse(url)
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=parsed.hostname) as s:
                s.settimeout(5)
                s.connect((parsed.hostname, 443))
                cert = s.getpeercert()
                expires = datetime.datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
                days_left = (expires - datetime.datetime.utcnow()).days
                if days_left < 10:
                    issues.append(f"{url} SSL expires in {days_left} days")

        except Exception as e:
            issues.append(f"{url} error: {str(e)}")
    if issues:
        return AuditResult("Endpoint Uptime / SSL", Severity.MEDIUM, issues)
    return None


# === TEST COVERAGE ===
def summarize_test_coverage():
    if os.path.exists("coverage.xml"):
        try:
            tree = ET.parse("coverage.xml")
            root = tree.getroot()
            coverage = root.attrib.get("line-rate")
            pct = round(float(coverage) * 100, 2)
            return AuditResult("Test Coverage", Severity.OK, [f"Line coverage: {pct}%"])
        except:
            return AuditResult("Test Coverage", Severity.LOW, ["Unable to parse coverage.xml"])
    return None


# === COST SPIKE ANOMALY ===
def detect_cost_spikes():
    path = ".snapcheck/cost_trend.json"
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        spikes = []
        prev = 0
        for day, cost in data.items():
            diff = float(cost) - prev
            if prev and diff > 20:
                spikes.append(f"{day} ➔ ${cost} (Δ${round(diff,2)})")
            prev = float(cost)
        if spikes:
            return AuditResult("Cost Spike Anomaly", Severity.HIGH, spikes)
    except:
        return None


# === HELPER EXTRACTION FUNCTIONS ===
def extract_ci_commits(ci_results):
    commits = set()
    for result in ci_results:
        for msg in result.messages:
            if "commit" in msg.lower():
                sha = msg.strip().split()[-1]
                if len(sha) == 7:
                    commits.add(sha)
    return commits

def extract_helm_mappings(helm_results):
    mappings = {}
    for result in helm_results:
        for msg in result.messages:
            if "chart version" in msg.lower() and "tag" in msg.lower():
                parts = msg.split()
                for part in parts:
                    if len(part) == 7:
                        mappings[part] = True
    return mappings

def extract_gitops_state(gitops_results):
    state = {}
    for result in gitops_results:
        sha = None
        app = "unknown"
        for msg in result.messages:
            if "revision" in msg.lower():
                for word in msg.split():
                    if len(word) == 7:
                        sha = word
            if "app" in msg.lower():
                app = msg.split()[-1]
        if sha:
            state[sha] = {"app": app}
    return state

def extract_k8s_problems(k8s_results):
    problems = {}
    for result in k8s_results:
        for msg in result.messages:
            if "crash" in msg.lower() or "failed" in msg.lower():
                problems[result.title] = msg
    return problems
