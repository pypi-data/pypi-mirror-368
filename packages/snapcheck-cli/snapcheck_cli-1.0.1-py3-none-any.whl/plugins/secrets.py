# plugins/secrets.py

import os, re, base64, datetime, requests
from kubernetes import client, config
from collections import defaultdict
from utils.reporter import AuditResult, Severity

GITHUB_API = "https://api.github.com"
SENSITIVE_KEYS = ["token", "password", "secret", "key", "apikey", "auth", "private"]

def get_github_secrets(repo, token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{GITHUB_API}/repos/{repo}/actions/secrets"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []
        return [s["name"] for s in response.json().get("secrets", [])]
    except:
        return []

def scan_github_workflows():
    used = set()
    wf_dir = os.path.join(".github", "workflows")
    if os.path.isdir(wf_dir):
        for file in os.listdir(wf_dir):
            if file.endswith((".yml", ".yaml")):
                with open(os.path.join(wf_dir, file), encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if "secrets." in line.lower():
                            used.update(re.findall(r"secrets\.([A-Z0-9_]+)", line))
    return list(used)

def scan_kubernetes_secrets(kubeconfig_path):
    try:
        config.load_kube_config(config_file=os.path.expanduser(kubeconfig_path))
        v1 = client.CoreV1Api()
    except:
        return None, None, None, None, "❌ Failed to load kubeconfig"

    sensitive, unused, ages, total = [], [], [], 0
    try:
        secrets = v1.list_secret_for_all_namespaces().items
        for secret in secrets:
            meta = secret.metadata
            if meta.name.startswith("default-token"):
                continue
            total += 1
            keys = list(secret.data.keys() if secret.data else [])

            if not keys:
                unused.append(f"{meta.namespace}/{meta.name} (empty)")
            if any(k for k in keys if any(s in k.lower() for s in SENSITIVE_KEYS)):
                sensitive.append(f"{meta.namespace}/{meta.name} ➤ keys: {keys}")
            age = (datetime.datetime.utcnow() - meta.creation_timestamp.replace(tzinfo=None)).days
            ages.append(f"{meta.namespace}/{meta.name} ➤ Age: {age}d")
    except Exception as e:
        return None, None, None, None, f"❌ Kubernetes API error: {e}"

    return total, sensitive, unused, ages, None

def scan_code_for_secrets(base="."):
    pattern = re.compile(r"(AWS|SECRET|TOKEN|PASSWORD|KEY)[\w\-]*\s*=\s*[\"']?[\w\-\/\+=]{8,}[\"']?", re.IGNORECASE)
    results = []
    for root, _, files in os.walk(base):
        for f in files:
            if f.endswith((".py", ".js", ".ts", ".env", ".sh", ".yaml", ".yml")):
                with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as file:
                    for i, line in enumerate(file):
                        if pattern.search(line):
                            results.append(f"{os.path.join(root, f)}:{i+1} ➤ {line.strip()}")
    return results

def run_check(config):
    test_mode = config.get("test_mode", False)
    if test_mode:
        return AuditResult(
            title="Secrets Audit",
            status=Severity.OK,
            messages=["Test mode enabled. Skipping GitHub/Kubernetes scans."]
        )

    repo = config.get("github_repo")
    token = config.get("github_token")
    kubeconfig = config.get("kubeconfig", "~/.kube/config")

    messages = []
    severity = Severity.OK

    # GitHub
    used = scan_github_workflows()
    inventory = get_github_secrets(repo, token) if repo and token else []
    unused_secrets = list(set(inventory) - set(used))
    messages.append(f"🔐 GitHub Secrets: {len(inventory)} total, {len(used)} used, {len(unused_secrets)} unused")

    if unused_secrets:
        severity = Severity.MEDIUM
        messages.extend([f"🔸 Unused: {', '.join(unused_secrets)}"])

    # Kubernetes
    total_k8s, sensitive_k8s, unused_k8s, age_info, err = scan_kubernetes_secrets(kubeconfig)
    if err:
        messages.append(err)
    else:
        messages.append(f"🔑 K8s Secrets: {total_k8s}, Sensitive: {len(sensitive_k8s)}, Unused: {len(unused_k8s)}")
        if sensitive_k8s:
            severity = Severity.HIGH
            messages.append(f"❗ Sensitive: {', '.join(sensitive_k8s[:5])}...")
        if unused_k8s:
            severity = max(severity, Severity.MEDIUM)
            messages.append(f"♻️ Unused: {', '.join(unused_k8s[:5])}...")

    # Codebase
    code_hits = scan_code_for_secrets()
    messages.append(f"🧬 Hardcoded secrets in codebase: {len(code_hits)}")
    if code_hits:
        severity = Severity.HIGH
        messages.append(f"🧨 Example: {code_hits[0]}")

    return AuditResult(
        title="Secrets Audit",
        status=severity,
        messages=messages
    )


