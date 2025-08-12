# SnapCheck — Unified DevOps/MLOps Audit & Correlation Engine

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![Build Status](https://img.shields.io/github/actions/workflow/status/gouthamyadavganta/snapcheck/build.yml?branch=main)]()
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()
[![Stars](https://img.shields.io/github/stars/gouthamyadavganta/snapcheck.svg?style=social)]()

> **One tool. One pass. Total visibility.**  
> SnapCheck is a modular, read-only audit platform for DevOps/MLOps estates.  
> It inspects Terraform, Kubernetes, Helm, CI/CD, Docker registries, secrets, AWS costs, and GitOps — then **correlates** signals to tell you *what broke, why, and what changed since last time*.

---

## 🌍 Why SnapCheck Exists

Modern engineering teams live across **10+ tools** — Terraform for infra, Kubernetes for workloads, GitHub for CI/CD, Helm for packaging, AWS Cost Explorer for finance, and so on.  
When something goes wrong, finding the *root cause* often means **hours of context switching** and digging through logs.

**SnapCheck fixes this by:**
- Pulling **signals from all your critical systems** in one pass.
- Correlating events into **human-readable storylines** (e.g., Terraform drift → Helm failure → CI/CD latency → cost anomaly).
- Producing **shareable, portable HTML & Markdown reports** for audits, reviews, and compliance.
- Enforcing **safe-by-default access** with OAuth + RBAC.

---

## 🚀 Core Features

| Capability | Highlights |
|------------|------------|
| **Terraform** | Local/remote `.tfstate`, drift detection, IAM wildcard/admin checks, stale resources, cost estimates |
| **Kubernetes** | Node readiness/pressure, pod health, restart spikes, PVC issues, DNS & service reachability, basic security context checks |
| **Helm** | List releases, detect failed upgrades, outdated charts, values drift |
| **CI/CD (GitHub)** | Longest jobs, average duration, flakiness, commit→deploy latency, branch protection enforcement |
| **Docker** | Remote registry scans (Docker Hub/GHCR), tags/manifests, metadata & CVEs |
| **Secrets** | GitHub Actions secrets, Kubernetes secrets, regex leak detection, age tracking |
| **Cost (AWS CE)** | Real monthly AWS spend by service, Terraform-managed vs unmanaged cost delta |
| **GitOps (Argo CD)** | App health, sync status, revision drift, failed syncs, auto-sync flag |
| **Correlation Engine** | Root cause vs symptom, regression detection, severity tagging |

---

## 🧰 Tech Stack (Quick Overview)

| Layer        | Tools & Libraries |
|--------------|-------------------|
| Core CLI     | Python 3.11+, Click, Rich, Jinja2 |
| Cloud APIs   | AWS boto3, GitHub REST API, Argo CD API |
| Kubernetes   | official `kubernetes` Python client |
| Security     | GitHub OAuth2, Starlette sessions, RBAC, JWT |
| Web UI       | FastAPI, TailwindCSS, Chart.js |
| Packaging    | pip, venv, Markdown, Mermaid |


---

## 🖥️ Architecture Overview

![Architecture Diagram](docs/img/architecture.png)

**How it works:**
1. `snapcheck run` loads a **profile** (YAML config for env, creds, modules).
2. Plugins run in parallel-ish to collect signals from their sources.
3. Correlation engine links findings into **storylines**.
4. Output generated in:
   - **Terminal**
   - **Markdown**
   - **HTML Dashboard** (Tailwind + Chart.js)
5. `.snapcheck/history/` stores past runs for trends & regression detection.

---

## 📦 Quick Start

```bash
## Install

### Recommended (pipx)
Requires Python 3.9+
```bash
pipx install snapcheck-cli
snapcheck --help

Upgrade

pipx upgrade snapcheck-cli

Uninstall

pipx uninstall snapcheck-cli
Windows note: If snapcheck isn’t found after install:

powershell

pipx ensurepath
then restart your terminal.

From source (for contributors)

git clone https://github.com/<your-org>/snapcheck.git
cd snapcheck
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate
pip install -e .
snapcheck --help

---

# 1. Create a profile
snapcheck init-profile --init-name prod --init-output profiles/prod.yaml --quickstart

# 2. Set environment variables
export SNAPCHECK_PROFILE=profiles/prod.yaml
export SNAPCHECK_OAUTH_CLIENT_ID=xxx
export SNAPCHECK_OAUTH_CLIENT_SECRET=xxx
export SNAPCHECK_SECRET_KEY="a_very_long_random"
export GITHUB_TOKEN="ghp_..."  # repo read + actions read

# Optional AWS/Argo creds
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export ARGOCD_TOKEN=...

---

# 3. Run audit
snapcheck run audit --modules all --output terminal

---

# 4. Serve dashboard
snapcheck serve --no-reload

---

📊 Example Audit Output

🚀 SnapCheck Audit Complete — 24 findings, 6 critical
Terraform: 3 drifted resources (S3 bucket public, IAM wildcard policy)
Kubernetes: 2 pods CrashLoopBackOff
AWS Cost: +45% this month (EC2 spike)
HTML Report:

---

🔐 Security & Compliance
Authentication: GitHub OAuth2 (scopes: read:user, user:email, read:org if org allowlist).

Authorization: RBAC via YAML (viewer, engineer, admin).

Secrets: Environment or vault only; no plaintext creds in repo.

Transport: TLS recommended; https_only: true in production.

Data at Rest: Reports can be kept offline or in private Pages/S3.

Audit Logging: Pluggable backends (file/SQLite/S3) for access events.

Full details: docs/security.md

---

📚 Documentation
Getting Started

Architecture

Profiles & Config

Operations & Runbooks

Plugin Reference

Security

FAQ

---

💡 Why Teams Use SnapCheck
Engineering: Faster root cause analysis across tool boundaries.

SRE: Audit and postmortem artifacts without piecing together CLI dumps.

Security: Early detection of leaks, public exposures, and stale secrets.

Leadership: Visibility into risk, cost anomalies, and trend regressions.

---

🤝 Contributing
We welcome issues, PRs, and discussions.
See docs/developer/contributing.md for details.

---

📜 License
MIT License — see LICENSE for details.

