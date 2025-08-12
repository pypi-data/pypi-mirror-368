import os
import json
from typing import Dict
from utils.reporter import AuditResult

SNAPSHOT_PATH = ".snapcheck/snapshot.json"

def load_previous_snapshot() -> Dict:
    if os.path.exists(SNAPSHOT_PATH):
        with open(SNAPSHOT_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_current_snapshot(data: Dict):
    os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)

    # Serialize AuditResult objects to dict
    serializable = {}
    for plugin, result in data.items():
        if isinstance(result, list):
            serializable[plugin] = [
                {"title": r.title, "status": r.status.value, "messages": r.messages}
                for r in result
                if isinstance(r, AuditResult)
            ]
        elif isinstance(result, AuditResult):
            serializable[plugin] = {
                "title": result.title,
                "status": result.status.value,
                "messages": result.messages
            }
        else:
            serializable[plugin] = result  # fallback (e.g., correlation dict)

    with open(SNAPSHOT_PATH, 'w') as f:
        json.dump(serializable, f, indent=2)

def compare_snapshots(prev: Dict, current: Dict) -> Dict:
    prev_set = set()
    curr_set = set()

    for plugin, results in prev.items():
        results_list = results if isinstance(results, list) else [results]
        for r in results_list:
            if isinstance(r, dict):
                status = r.get('status', 'unknown')
                messages = r.get('messages', [])
                msg = f"{plugin}:{status}:{' | '.join(messages)}"
                prev_set.add(msg)

    for plugin, results in current.items():
        results_list = results if isinstance(results, list) else [results]
        for r in results_list:
            if isinstance(r, AuditResult):
                msg = f"{plugin}:{r.status.value}:{' | '.join(r.messages)}"
                curr_set.add(msg)

    new_issues = curr_set - prev_set
    resolved_issues = prev_set - curr_set

    messages = []
    regressions = []

    for issue in new_issues:
        messages.append(f"🆕 New issue: {issue}")
        if ":high:" in issue or ":critical:" in issue:
            regressions.append(issue)

    for issue in resolved_issues:
        messages.append(f"✅ Resolved: {issue}")

    return {
        "messages": messages,
        "regressions": regressions
    }
