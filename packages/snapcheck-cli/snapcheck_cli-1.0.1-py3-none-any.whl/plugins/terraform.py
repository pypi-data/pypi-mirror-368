import os
import datetime
import re
import json
from collections import defaultdict
from rich import print
from utils.reporter import AuditResult, Severity


def parse_tfstate(state_path):
    try:
        if state_path.startswith("s3://"):
            import boto3
            bucket_key = state_path.replace("s3://", "")
            bucket, _, key = bucket_key.partition("/")
            s3 = boto3.client("s3")
            obj = s3.get_object(Bucket=bucket, Key=key)
            return json.loads(obj["Body"].read().decode("utf-8"))

        elif state_path.startswith("http://") or state_path.startswith("https://"):
            import requests
            resp = requests.get(state_path)
            resp.raise_for_status()
            return resp.json()

        else:
            with open(state_path, "r") as f:
                return json.load(f)

    except Exception as e:
        print(f"[red]Failed to load terraform state: {e}[/red]")
        return None


def get_state_age(state_path):
    try:
        if state_path.startswith("s3://") or state_path.startswith("http"):
            return "Remote"
        timestamp = os.path.getmtime(state_path)
        return (datetime.datetime.now() - datetime.datetime.fromtimestamp(timestamp)).days
    except Exception:
        return "Unknown"


def find_admin_iam_roles(tfstate):
    admin_roles = []
    for resource in tfstate.get("resources", []):
        if resource["type"] == "aws_iam_role":
            for instance in resource.get("instances", []):
                policy_doc = instance["attributes"].get("assume_role_policy", "")
                if "AdministratorAccess" in policy_doc or '"Action":"*"' in policy_doc:
                    admin_roles.append(resource["name"])
    return admin_roles


def find_old_resources(tfstate, days=90):
    old_resources = []
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    for resource in tfstate.get("resources", []):
        for instance in resource.get("instances", []):
            created = instance.get("attributes", {}).get("created_time")
            if created:
                try:
                    created_dt = datetime.datetime.fromisoformat(created)
                    if created_dt < cutoff:
                        old_resources.append(resource["name"])
                except Exception:
                    continue
    return old_resources


def find_unreferenced_outputs(tfstate):
    unreferenced = []
    outputs = tfstate.get("outputs", {})
    for name, output in outputs.items():
        if not output.get("value"):
            unreferenced.append(name)
    return unreferenced


def find_hardcoded_secrets():
    suspicious_lines = []
    for root, _, files in os.walk("."):
        for f in files:
            if f.endswith(".tf"):
                try:
                    with open(os.path.join(root, f), "r", errors="ignore") as file:
                        for i, line in enumerate(file.readlines()):
                            if re.search(r"(aws_|github_)?secret|access|token|key", line, re.IGNORECASE):
                                suspicious_lines.append(f"{f}:{i+1} - {line.strip()}")
                except:
                    continue
    return suspicious_lines


def detect_wildcard_iam_policies(tfstate):
    wildcards = []
    for resource in tfstate.get("resources", []):
        if resource["type"] == "aws_iam_policy":
            for instance in resource.get("instances", []):
                policy = instance["attributes"].get("policy", "")
                if '*"' in policy:
                    wildcards.append(resource["name"])
    return wildcards


def detect_public_resources(tfstate):
    public = []
    for resource in tfstate.get("resources", []):
        if resource["type"] == "aws_s3_bucket_policy":
            for instance in resource.get("instances", []):
                policy = instance["attributes"].get("policy", "")
                if '"Principal": "*"' in policy:
                    public.append(resource["name"])
        if resource["type"] == "aws_security_group":
            for instance in resource.get("instances", []):
                ingress = instance["attributes"].get("ingress", [])
                for rule in ingress:
                    cidrs = rule.get("cidr_blocks", [])
                    if "0.0.0.0/0" in cidrs:
                        public.append(resource["name"])
    return public


def count_resource_types(tfstate):
    counter = defaultdict(int)
    for resource in tfstate.get("resources", []):
        counter[resource["type"]] += 1
    return dict(counter)


def estimate_cost_from_state(tfstate):
    est = 0
    for resource in tfstate.get("resources", []):
        rtype = resource["type"]
        if rtype == "aws_instance":
            est += 20
        elif rtype == "aws_s3_bucket":
            est += 5
        elif rtype == "aws_rds_instance":
            est += 100
    return f"${est}/mo (rough estimate based on resource types)"


def find_unused_modules():
    used_modules = set()
    declared_modules = set()

    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".tf"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", errors="ignore") as f:
                        content = f.read()
                        declared_modules.update(re.findall(r'module\s+"(.*?)"', content))
                        used_modules.update(re.findall(r"module\.(\w+)", content))
                except:
                    continue

    return list(declared_modules - used_modules)


def run_check(config):
    state_path = config.get("terraform_state", "./terraform/terraform.tfstate")
    tfstate = parse_tfstate(state_path)
    if not tfstate:
        return [AuditResult("Terraform State", Severity.CRITICAL, ["Unable to read tfstate or file not found."])]

    drifted = []  # Placeholder — real drift is in correlator
    state_age = get_state_age(state_path)
    admin_roles = find_admin_iam_roles(tfstate)
    old = find_old_resources(tfstate)
    outputs = find_unreferenced_outputs(tfstate)
    secrets = find_hardcoded_secrets()
    wildcards = detect_wildcard_iam_policies(tfstate)
    public = detect_public_resources(tfstate)
    resource_count = count_resource_types(tfstate)
    estimated_cost = estimate_cost_from_state(tfstate)
    unused_modules = find_unused_modules()

    results = []

    if drifted:
        results.append(AuditResult("Terraform Drift", Severity.HIGH, drifted))
    if admin_roles:
        results.append(AuditResult("Admin IAM Roles", Severity.HIGH, admin_roles))
    if old:
        results.append(AuditResult("Old Resources", Severity.MEDIUM, old))
    if outputs:
        results.append(AuditResult("Unreferenced Outputs", Severity.LOW, outputs))
    if secrets:
        results.append(AuditResult("Hardcoded Secrets", Severity.HIGH, secrets))
    if wildcards:
        results.append(AuditResult("Wildcard IAM Policies", Severity.HIGH, wildcards))
    if public:
        results.append(AuditResult("Publicly Accessible Resources", Severity.HIGH, public))
    if unused_modules:
        results.append(AuditResult("Unused Modules", Severity.LOW, unused_modules))

    results.append(AuditResult("Terraform Cost Estimate", Severity.OK, [estimated_cost]))
    results.append(AuditResult("State Age", Severity.OK, [f"{state_age} days"] if isinstance(state_age, int) else [str(state_age)]))
    results.append(AuditResult("Terraform Resource Types", Severity.OK, [f"{k}: {v}" for k, v in resource_count.items()]))

    return results



