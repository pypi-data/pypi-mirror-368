# main.py
# ─────────────────────────────────────────────────────────────────────────────
# SnapCheck CLI Entrypoint
# Clean, standardized Click-based CLI with clear command grouping.
# - run audit / run full-audit
# - serve (FastAPI UI)
# - publish (GitHub Pages)
# - list-plugins / version / init-profile
# ─────────────────────────────────────────────────────────────────────────────

import os
import sys
import click
from pathlib import Path
from datetime import datetime

# ── Bootstrap sys.path for local package imports
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ── Core Imports
from rich.console import Console
from rich.table import Table

from config.config_loader import load_config
from plugins import terraform, kubernetes, helm, ci_cd, docker, secrets, cost, gitops
from output.markdown_report import save_markdown_report
from output.html_report import generate_html_report
from core.correlator import correlate
from core.snapshot_diff import load_previous_snapshot, compare_snapshots, save_current_snapshot
from core.explain import generate_gpt_summary
from utils.secret_loader import SecretLoader
from utils.publisher import publish_report
from utils.reporter import save_audit_result_json, AuditResult, Severity
from cli.init_profile import generate_profile
from utils.sanitize import deep_mask  # 🔒 universal masking for terminal/markdown only

# ── Constants
VERSION = "1.0.0"
console = Console()

# ── Module dispatch map
MODULE_MAP = {
    "terraform": terraform.run_check,
    "kubernetes": kubernetes.run_check,
    "helm": helm.run_check,
    "ci_cd": ci_cd.run_check,
    "docker": docker.run_check,
    "secrets": secrets.run_check,
    "cost": cost.run_check,
    "gitops": gitops.check_gitops,
}

# ─────────────────────────────────────────────────────────────────────────────
# Top-level Click group
# ─────────────────────────────────────────────────────────────────────────────
@click.group(help="SnapCheck - Modular DevOps/MLOps Audit CLI")
def cli():
    pass

# ─────────────────────────────────────────────────────────────────────────────
# Utility Commands
# ─────────────────────────────────────────────────────────────────────────────
@cli.command(help="Show SnapCheck version")
def version():
    console.print(f"🔖 SnapCheck Version: [bold green]{VERSION}[/bold green]")

@cli.command(help="List available plugin modules")
def list_plugins():
    console.print("\n🧩 [bold cyan]Available Plugins:[/bold cyan]")
    for mod in MODULE_MAP:
        console.print(f"  - {mod}")

@cli.command(help="Generate a sample profile YAML (use --quickstart for a pre-filled template)")
@click.option('--init-name', default="default-cluster", show_default=True, help="Name to use in generated profile")
@click.option('--init-output', default="profiles/sample.yaml", show_default=True, help="Path to save generated profile")
@click.option('--quickstart', is_flag=True, help="Write a pre-filled quickstart profile template")
def init_profile(init_name, init_output, quickstart):
    """
    Backward-compatible profile generator.
    - Default behavior: uses cli.init_profile.generate_profile (unchanged).
    - --quickstart: writes a pre-filled, ready-to-edit template here in main.py (no dependency changes).
    """
    if not quickstart:
        # Keep existing working logic untouched
        generate_profile(profile_name=init_name, output_path=init_output)
        console.print(f"[green]✅ Profile generated at[/green] {init_output}")
        return

    # Quickstart path (new, additive) — matches load_config() schema
    import yaml
    os.makedirs(os.path.dirname(init_output), exist_ok=True)

    quickstart_template = {
        "name": init_name,
        "aws_region": "us-east-1",
        "secrets_source": "env",
        "env_secrets": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "GITHUB_TOKEN", "ARGOCD_TOKEN"],
        "modules": ["terraform", "kubernetes", "helm", "ci_cd", "docker", "secrets", "cost", "gitops"],
        "terraform_state": "./state.tfstate",
        "kubeconfig": "~/.kube/config",
        "helm_namespaces": ["default", "monitoring"],
        "ci_platform": "github",
        "github_repo": "username/repo",
        "docker_images": ["username/image:latest"],
        "gitops": {"method": "api", "argocd_server": "https://argo.example.com", "test_mode": True},
        "publishing": {"github_repo": "username/repo", "history": True},
        "mask_secrets": True,
        "demo_mode": True,
        "security": {
            "enabled": True,
            "allowed_emails": ["you@company.com"],
            "allowed_orgs": [],
            "rbac": {"you@company.com": "admin", "*": "viewer"},
            "session": {"https_only": True, "cookie_name": "snapcheck_session"},
            "watermark": "Confidential – SnapCheck",
            "share": {"enabled": True, "ttl_minutes": 60}
        }
    }

    with open(init_output, "w", encoding="utf-8") as f:
        yaml.safe_dump(quickstart_template, f, sort_keys=False)

    console.print(f"[green]✅ Quickstart profile created at[/green] {init_output}")
    console.print("[cyan]Next:[/cyan] Edit repo names/URLs and run:  [bold]snapcheck run --profile[/bold]")

# ─────────────────────────────────────────────────────────────────────────────
# Serve (Web UI)
# ─────────────────────────────────────────────────────────────────────────────
@cli.command(help="Serve the latest SnapCheck report with the Web UI (FastAPI)")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, type=int, show_default=True)
@click.option("--reload/--no-reload", default=True, show_default=True)
def serve(host, port, reload):
    """Run FastAPI app that serves .snapcheck/report.html with client-side UI."""
    try:
        import uvicorn  # lazy import to keep startup fast for other commands
    except ImportError:
        console.print("[red]❌ uvicorn not installed. Run: pip install 'uvicorn[standard]'[/red]")
        raise SystemExit(1)

    console.print(f"Serving SnapCheck UI at [bold]http://{host}:{port}[/bold]")
    # This targets web/server.py -> app = FastAPI(...)
    uvicorn.run("web.server:app", host=host, port=port, reload=reload)

# ─────────────────────────────────────────────────────────────────────────────
# Publish (GitHub Pages)
# ─────────────────────────────────────────────────────────────────────────────
@cli.command(help="Publish SnapCheck report to GitHub Pages (with optional history index)")
@click.option('--profile', default="profiles/prod.yaml", show_default=True, help="Path to the profile YAML")
@click.option('--with-history', is_flag=True, help="Also (re)generate index for archived reports")
def publish(profile, with_history):
    # generate index if requested (kept here if you later add utils.publisher.generate_report_index)
    if with_history:
        try:
            from utils.publisher import generate_report_index
            generate_report_index(".snapcheck")
            console.print("[green]✅ History index generated[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not generate history index: {e}[/yellow]")

    publish_report(profile)
    console.print("[green]✅ Publish complete[/green]")

# ─────────────────────────────────────────────────────────────────────────────
# Run Group
# ─────────────────────────────────────────────────────────────────────────────
@cli.group(help="Run SnapCheck audits")
def run():
    pass

@run.command("audit", help="Run SnapCheck audit (selected modules)")
@click.option('--profile', default="profiles/prod.yaml", show_default=True, help="Path to the profile YAML")
@click.option('--modules', default="all", show_default=True, help="Comma-separated list of modules to run or 'all'")
@click.option('--output', default="terminal", show_default=True,
              type=click.Choice(["terminal", "markdown"]), help="Output format")
@click.option('--fail-on', default=None, type=click.Choice(["none", "warn", "fail"]), show_default=False,
              help="Optional: set non-zero exit if WARN/FAIL present (security-friendly).")
def audit(profile, modules, output, fail_on):
    console.print("🚀 [bold green]SnapCheck Audit Starting...[/bold green]\n")

    # ── Load profile & secrets
    try:
        config = load_config(profile)
        loader = SecretLoader(config)
        config["secret_loader"] = loader

        # Hydrate env vars if provided via secret loader
        for key in config.get("env_secrets", []):
            if not os.getenv(key):
                val = loader.get(key)
                if val:
                    os.environ[key] = str(val)

    except Exception as e:
        console.print(f"[red]❌ Failed to load profile or secrets: {e}[/red]")
        return

    # ── Resolve modules (fallback to all MODULE_MAP keys if profile has none)
    selected_modules = (
        config.get("modules", []) if modules == "all"
        else [m.strip() for m in modules.split(",")]
    )
    if modules == "all" and not selected_modules:
        selected_modules = list(MODULE_MAP.keys())

    # ── Safety notice for GitOps plugin
    if "gitops" in selected_modules:
        gitops_config = config.get("gitops", {})
        if not gitops_config.get("argocd_server") and not gitops_config.get("test_mode", False):
            console.print("[yellow]⚠️ GitOps plugin enabled, but no ArgoCD server or test_mode is configured.[/yellow]")

    # ── Run plugins
    results = {}
    for module in selected_modules:
        run_fn = MODULE_MAP.get(module)
        if not run_fn:
            results[module] = AuditResult(module.title(), Severity.UNKNOWN, ["Module not found"])
            continue

        try:
            console.print(f"🔍 [cyan]Running {module} check...[/cyan]")
            result = run_fn(config)

            # Normalize to AuditResult or list[AuditResult]
            if isinstance(result, str):
                result = AuditResult(module.title(), Severity.CRITICAL, [result])

            results[module] = result

            # Save JSON snapshot (per result)
            if isinstance(result, list):
                for idx, r in enumerate(result):
                    save_audit_result_json(f"{module}_{idx}", r)
            elif hasattr(result, "status"):
                save_audit_result_json(module, result)

        except Exception as e:
            err_result = AuditResult(module.title(), Severity.CRITICAL, [f"Exception: {str(e)}"])
            results[module] = err_result
            save_audit_result_json(module, err_result)

    # ── Correlation & snapshot diff
    correlation_result = correlate(results)
    results["correlation"] = correlation_result
    if isinstance(correlation_result, list):
        for idx, r in enumerate(correlation_result):
            save_audit_result_json(f"correlation_{idx}", r)
    elif isinstance(correlation_result, AuditResult):
        save_audit_result_json("correlation", correlation_result)

    prev = load_previous_snapshot()
    diff_results = compare_snapshots(prev, results)
    save_current_snapshot(results)

    # ── GPT summary (optional)
    gpt_summary = generate_gpt_summary(results)

    # ── Summary & charts (placeholder defaults; your plugins can populate richer data)
    summary_data = {
        "pass": sum(1 for items in results.values() if isinstance(items, list)
                    for i in items if getattr(i, "status", None) and getattr(i.status, "value", "").lower() == "pass"),
        "fail": sum(1 for items in results.values() if isinstance(items, list)
                    for i in items if getattr(i, "status", None) and getattr(i.status, "value", "").lower() in ["high", "critical"]),
        "regressions": len(diff_results["regressions"]) if diff_results else 0,
    }

    charts_data = {
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
                "data": [30, 45, 20],
                "backgroundColor": ["#6366F1", "#EC4899", "#10B981"]
            }]
        }
    }

    # ── Optional branding from profile (used by header in the HTML template)
    branding = (config.get("branding") or {})
    if branding:
        summary_data["brand_title"] = branding.get("title")
        summary_data["brand_logo_url"] = branding.get("logo_url")
        summary_data["brand_subtitle"] = branding.get("subtitle")
        summary_data["brand_link"] = branding.get("link")

    # ── HTML report (HTML masking is selective inside html_report.py)
    generate_html_report(
        plugin_results=results,
        summary=summary_data,
        charts=charts_data,
        gpt_summary=gpt_summary,
        diff=diff_results if diff_results else {},
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        out_path=".snapcheck/report.html"
    )

    # ── Terminal/Markdown output
    mask_enabled = True if config.get("mask_secrets", True) else False

    if output == "terminal":
        # Prepare a minimal structure to mask, then display
        terminal_rows = []
        for mod, result in results.items():
            summary = (
                result[0].status.value if isinstance(result, list) and result and hasattr(result[0], "status") else
                result.status.value if hasattr(result, "status") else
                str(result)
            )
            terminal_rows.append((mod, summary))

        # Apply universal masking to any strings that might include secrets
        if mask_enabled:
            safe_rows = []
            for mod, summary in terminal_rows:
                masked_mod = deep_mask(mod)
                masked_summary = deep_mask(summary)
                safe_rows.append((masked_mod, masked_summary))
            terminal_rows = safe_rows

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Module", width=15)
        table.add_column("Status", style="green")
        for mod, status in terminal_rows:
            table.add_row(mod, status)

        console.print("\n📊 [bold cyan]Audit Results:[/bold cyan]")
        console.print(table)

    elif output == "markdown":
        # markdown_report.save_markdown_report internally applies deep_mask
        filename = save_markdown_report(profile, results)
        console.print(f"\n📄 [bold green]Report saved:[/bold green] {filename}")

    # ── Optional security-friendly exit code (non-breaking default behavior)
    if fail_on:
        # Evaluate overall state for exit codes
        has_warn = False
        has_fail = False
        for mod, res in results.items():
            items = res if isinstance(res, list) else [res]
            for it in items:
                status_val = getattr(getattr(it, "status", None), "value", str(getattr(it, "status", "info"))).upper()
                if status_val in ("WARN", "WARNING", "LOW", "MEDIUM"):
                    has_warn = True
                if status_val in ("FAIL", "HIGH", "CRITICAL", "ERROR", "SEVERE"):
                    has_fail = True

        if fail_on == "warn" and (has_warn or has_fail):
            raise SystemExit(2)
        if fail_on == "fail" and has_fail:
            raise SystemExit(3)

@run.command("full-audit", help="Run full audit with all enabled modules (shortcut)")
@click.option('--profile', required=True, help="Path to the profile YAML")
def full_audit(profile):
    ctx = click.get_current_context()
    ctx.invoke(audit, profile=profile, modules="all", output="terminal")

# ─────────────────────────────────────────────────────────────────────────────
# Demo (canned results; no plugins invoked)
# ─────────────────────────────────────────────────────────────────────────────
@cli.command(help="Generate a demo report without calling any plugins")
@click.option('--profile', default="profiles/demo.yaml", show_default=True, help="Path to the profile YAML (optional)")
def demo(profile):
    # Lazy imports to avoid touching working paths unless used
    try:
        cfg = load_config(profile)
    except Exception:
        cfg = {"demo_mode": True}

    # Use canned fixtures
    from utils.demo_fixtures import get_demo_results, get_demo_summary_and_charts

    results = get_demo_results(cfg)
    summary_data, charts_data = get_demo_summary_and_charts(results)

    # Optional GPT summary (static, safe)
    gpt_summary = "Demo summary: No critical issues. Minor Helm update available. Watch pod restarts in monitoring."

    # Mask plugin outputs for other channels; HTML handles masking selectively
    safe_results = deep_mask(results)
    summary_data["demo_mode"] = True

    # Pass branding from profile to summary for header/logo
    branding = (cfg.get("branding") or {})
    if branding:
        summary_data["brand_title"] = branding.get("title")
        summary_data["brand_logo_url"] = branding.get("logo_url")
        summary_data["brand_subtitle"] = branding.get("subtitle")
        summary_data["brand_link"] = branding.get("link")

    # HTML report
    generate_html_report(
        plugin_results=safe_results,
        summary=summary_data,
        charts=charts_data,
        gpt_summary=gpt_summary,
        diff={},
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        out_path=".snapcheck/report.html"
    )

    # Markdown report
    filename = save_markdown_report(profile, safe_results)

    console.print("[green]✅ Demo report generated[/green]")
    console.print(f"  • HTML: .snapcheck{os.sep}report.html")
    console.print(f"  • Markdown: {filename}")

# ─────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cli()