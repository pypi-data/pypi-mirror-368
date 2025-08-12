
import requests
import datetime
import os
from collections import defaultdict
import statistics

GITHUB_API = "https://api.github.com"

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

def get_recent_workflow_runs(repo, headers, limit=10):
    url = f"{GITHUB_API}/repos/{repo}/actions/runs"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Failed to fetch workflow runs: {resp.text}")
    return resp.json().get("workflow_runs", [])[:limit]

def get_jobs_for_run(repo, run_id, headers):
    url = f"{GITHUB_API}/repos/{repo}/actions/runs/{run_id}/jobs"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return []
    return resp.json().get("jobs", [])

def get_artifacts(repo, headers):
    url = f"{GITHUB_API}/repos/{repo}/actions/artifacts"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return []
    return resp.json().get("artifacts", [])

def get_branch_protection(repo, headers, branch="main"):
    url = f"{GITHUB_API}/repos/{repo}/branches/{branch}/protection"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return True
    elif resp.status_code == 404:
        return False
    else:
        raise Exception(f"Error checking branch protection: {resp.text}")

def analyze_runs(repo, runs, headers):
    total_duration = 0
    longest_job = {"name": "", "duration": 0}
    contributors = defaultdict(int)
    flaky_jobs = 0
    failed_runs = 0
    artifact_sizes = []
    secrets_used = set()
    commit_latencies = []
    artifact_trend = []
    bot_triggers = 0

    for run in runs:
        created_at = datetime.datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
        updated_at = datetime.datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
        duration = (updated_at - created_at).total_seconds() / 60
        total_duration += duration

        if run.get("conclusion") == "failure":
            failed_runs += 1
        if duration > 30:
            flaky_jobs += 1

        actor = run.get("triggering_actor", {}).get("login", "unknown")
        contributors[actor] += 1

        if "bot" in actor.lower():
            bot_triggers += 1

        jobs = get_jobs_for_run(repo, run["id"], headers)
        for job in jobs:
            started = job.get("started_at")
            completed = job.get("completed_at")
            if started and completed:
                s = datetime.datetime.fromisoformat(started.replace("Z", "+00:00"))
                c = datetime.datetime.fromisoformat(completed.replace("Z", "+00:00"))
                job_duration = (c - s).total_seconds() / 60
                if job_duration > longest_job["duration"]:
                    longest_job = {"name": job["name"], "duration": round(job_duration, 2)}

        head_commit_time = run.get("run_started_at")
        if head_commit_time:
            commit_time = datetime.datetime.fromisoformat(head_commit_time.replace("Z", "+00:00"))
            latency = (updated_at - commit_time).total_seconds() / 60
            commit_latencies.append(latency)

    artifacts = get_artifacts(repo, headers)
    for art in artifacts:
        size_mb = round(art["size_in_bytes"] / 1024 / 1024, 2)
        artifact_sizes.append(size_mb)
        created_at = art["created_at"]
        artifact_trend.append((created_at, size_mb))

    workflows_dir = os.path.join(".github", "workflows")
    if os.path.isdir(workflows_dir):
        for fname in os.listdir(workflows_dir):
            if fname.endswith(".yml") or fname.endswith(".yaml"):
                with open(os.path.join(workflows_dir, fname), "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if "secrets." in line:
                            secrets_used.add(line.strip())

    avg_duration = round(total_duration / len(runs), 1) if runs else 0
    avg_latency = round(sum(commit_latencies) / len(commit_latencies), 1) if commit_latencies else 0
    artifact_stats = (
        f"{len(artifact_sizes)} artifacts, avg size: {round(statistics.mean(artifact_sizes), 2)} MB" 
        if artifact_sizes else "No artifacts"
    )

    return {
        "total_runs": len(runs),
        "failed_runs": failed_runs,
        "longest_job": longest_job,
        "avg_duration_min": avg_duration,
        "avg_latency_min": avg_latency,
        "contributors": dict(contributors),
        "flaky_jobs": flaky_jobs,
        "secrets_used": list(secrets_used),
        "artifact_summary": artifact_stats,
        "artifact_trend": artifact_trend,
        "bot_triggered_jobs": bot_triggers
    }

def run_check(config):
    repo = config.get("github_repo")
    token = config.get("github_token")
    if not repo or not token:
        return "❌ GitHub repo or token missing in config"

    try:
        headers = get_headers(token)
        runs = get_recent_workflow_runs(repo, headers)
        metrics = analyze_runs(repo, runs, headers)
        branch_protected = get_branch_protection(repo, headers)

        summary = (
            f"{metrics['failed_runs']} failures, {metrics['flaky_jobs']} flaky, "
            f"{metrics['avg_duration_min']}m avg, longest: {metrics['longest_job']['name']}, "
            f"{metrics['bot_triggered_jobs']} bot jobs, branch protection: {'✅' if branch_protected else '❌'}"
        )
        return summary, metrics

    except Exception as e:
        return f"❌ GitHub API Error: {str(e)}"
