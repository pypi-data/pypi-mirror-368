import os
import re
import shutil
from datetime import datetime
from git import Repo
from config.config_loader import load_config
from utils.logger import logger
from jinja2 import Environment, FileSystemLoader

def redact_secrets(content: str) -> str:
    patterns = [
        r'AKIA[0-9A-Z]{16}',           # AWS Access Key
        r'ASIA[0-9A-Z]{16}',           # AWS Temp Key
        r'ghp_[A-Za-z0-9]{36,}',       # GitHub Personal Token
        r'sk_live_[A-Za-z0-9]{24,}',   # Stripe keys
        r'(?i)secret[^a-z0-9]?["\']?[\w\d]{10,}'  # generic
    ]
    for pattern in patterns:
        content = re.sub(pattern, '***REDACTED***', content)
    return content

def backup_report_locally(report_path: str):
    backup_dir = os.path.join("reports")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(backup_dir, f"report-{timestamp}.html")

    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    redacted = redact_secrets(content)
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(redacted)

    logger.info(f"📦 Report backup saved to: {backup_path}")
    return backup_path

def publish_report(profile_path: str):
    try:
        config = load_config(profile_path)

        github_repo = config.get("github_repo")
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_repo or not github_token:
            raise ValueError("Missing github_repo in config or GITHUB_TOKEN in environment")

        local_repo_path = os.getcwd()
        gh_pages_path = os.path.join(local_repo_path, "gh-pages-temp")

        # Clean temp folder
        if os.path.exists(gh_pages_path):
            shutil.rmtree(gh_pages_path)

        # Clone gh-pages branch
        repo_url = f"https://{github_token}@github.com/{github_repo}.git"
        repo = Repo.clone_from(repo_url, gh_pages_path)
        try:
            repo.git.checkout("gh-pages")
        except:
            repo.git.checkout("-b", "gh-pages")

        # Copy redacted .html files
        snapcheck_dir = os.path.join(local_repo_path, ".snapcheck")
        html_files = [f for f in os.listdir(snapcheck_dir) if f.endswith(".html")]
        if not html_files:
            raise FileNotFoundError("No HTML reports found in .snapcheck")

        for file in html_files:
            src_path = os.path.join(snapcheck_dir, file)
            with open(src_path, "r", encoding="utf-8") as f:
                content = f.read()
            redacted = redact_secrets(content)
            with open(os.path.join(gh_pages_path, file), "w", encoding="utf-8") as f:
                f.write(redacted)

        # Commit and push
        repo.index.add([f for f in os.listdir(gh_pages_path) if f.endswith(".html")])
        repo.index.commit("📊 Publish SnapCheck report(s)")
        repo.remote().push(refspec="gh-pages:gh-pages")

        url = f"https://{github_repo.split('/')[0]}.github.io/{github_repo.split('/')[1]}/index.html"
        logger.info(f"✅ Published to GitHub Pages: {url}")

        # Backup locally
        backup_report_locally(os.path.join(snapcheck_dir, "report.html"))

    except Exception as e:
        logger.error(f"❌ Failed to publish to GitHub Pages: {e}")
        try:
            fallback_path = os.path.join(".snapcheck", "report.html")
            if os.path.exists(fallback_path):
                backup_report_locally(fallback_path)
        except Exception as be:
            logger.error(f"❌ Even backup failed: {be}")

def generate_report_index(output_dir=".snapcheck"):
    try:
        env = Environment(loader=FileSystemLoader("output/templates"))
        template = env.get_template("report_index.html")

        report_files = sorted([
            f for f in os.listdir(output_dir)
            if f.startswith("report-") and f.endswith(".html")
        ], reverse=True)

        index_path = os.path.join(output_dir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(template.render(reports=report_files))

        logger.info(f"📄 Generated index.html with {len(report_files)} reports")

    except Exception as e:
        logger.error(f"❌ Failed to generate index.html: {e}")

