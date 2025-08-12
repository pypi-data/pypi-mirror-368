# plugins/docker.py

import requests
from utils.reporter import AuditResult, Severity

DOCKER_HUB_API = "https://hub.docker.com/v2"

def get_dockerhub_tags(image_name):
    try:
        url = f"{DOCKER_HUB_API}/repositories/{image_name}/tags?page_size=100"
        response = requests.get(url)
        if response.status_code != 200:
            return []
        return response.json().get("results", [])
    except Exception:
        return []

def get_vulnerabilities(image_name, tag="latest"):
    # Simulated CVE count — Replace with real scanner API later
    return {
        "critical": 3,
        "high": 8,
        "medium": 12,
        "low": 5
    }

def run_check(config):
    test_mode = config.get("test_mode", False)
    if test_mode:
        return AuditResult(
            title="Docker Image Audit",
            status=Severity.OK,
            messages=["Test mode enabled. Skipping DockerHub scan."]
        )

    images = config.get("docker_images", [{"name": "library/nginx", "tags": ["latest"]}])
    messages = []
    severity = Severity.OK

    for image in images:
        name = image.get("name")
        tags = image.get("tags", ["latest"])
        try:
            messages.append(f"📦 Scanning image: {name} ➤ Tags: {', '.join(tags)}")
            available_tags = get_dockerhub_tags(name)

            for tag in tags:
                matched = next((t for t in available_tags if t["name"] == tag), {})
                size = round((matched.get("full_size", 0) / 1024 / 1024), 2) if matched else "?"
                os_list = list({img["os"] for img in matched.get("images", [])}) if matched else []

                cves = get_vulnerabilities(name, tag)
                msg = (
                    f"{name}:{tag} ➤ {size}MB | "
                    f"CVEs: 🔴 {cves['critical']}  🔶 {cves['high']}  🟡 {cves['medium']}  🟢 {cves['low']}"
                )
                messages.append(msg)

                # Update severity
                if cves["critical"] >= 1:
                    severity = Severity.CRITICAL
                elif cves["high"] >= 3:
                    severity = Severity.HIGH
                elif cves["medium"] >= 5:
                    severity = Severity.MEDIUM

        except Exception as e:
            messages.append(f"❌ Error scanning {name}: {str(e)}")
            severity = Severity.CRITICAL

    return AuditResult(
        title="Docker Image Audit",
        status=severity,
        messages=messages
    )

