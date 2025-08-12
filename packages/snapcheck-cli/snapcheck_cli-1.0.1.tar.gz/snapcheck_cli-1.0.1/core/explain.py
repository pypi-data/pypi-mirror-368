import os
from openai import OpenAI
from typing import Dict
from utils.reporter import AuditResult

def generate_gpt_summary(audit_data: Dict, max_tokens: int = 250) -> str:
    """
    Uses OpenAI GPT to generate a human-readable summary of audit results.
    Works with AuditResult objects and dicts.
    Requires OPENAI_API_KEY to be set as an environment variable.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "GPT summary not available. Set OPENAI_API_KEY."

    client = OpenAI(api_key=api_key)

    try:
        summary_lines = []

        for plugin, results in audit_data.items():
            if isinstance(results, list):
                for r in results:
                    if isinstance(r, AuditResult):
                        severity = r.status.value
                        messages = " | ".join([m for m in r.messages if m.strip()])
                    elif isinstance(r, dict):
                        severity = r.get("severity", "low")
                        messages = r.get("message", "").strip()
                    else:
                        continue
                    if messages:
                        summary_lines.append(f"[{plugin}] {severity.upper()}: {messages}")

            elif isinstance(results, AuditResult):
                messages = " | ".join([m for m in results.messages if m.strip()])
                if messages:
                    summary_lines.append(f"[{plugin}] {results.status.value.upper()}: {messages}")

            elif isinstance(results, dict):
                severity = results.get("severity", "low")
                messages = results.get("message", "").strip()
                if messages:
                    summary_lines.append(f"[{plugin}] {severity.upper()}: {messages}")

        if not summary_lines:
            return "No audit findings to summarize."

        prompt_input = "\n".join(summary_lines[:50])
        prompt = (
            "You are a senior SRE. Read the following audit findings and summarize:\n"
            "- Key issues\n"
            "- Likely root causes\n"
            "- Possible impact\n"
            "- Any cost spikes or infra drift\n"
            f"\n{prompt_input}\n"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful DevOps summarizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ GPT summary generation failed: {str(e)}"

