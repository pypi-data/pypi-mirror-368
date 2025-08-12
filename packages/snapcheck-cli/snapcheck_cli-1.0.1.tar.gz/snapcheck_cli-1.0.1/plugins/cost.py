# plugins/cost.py

import boto3
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from utils.reporter import AuditResult, Severity

def emoji(cost):
    if cost > 500:
        return "🛑"
    elif cost > 200:
        return "🔴"
    elif cost > 100:
        return "🟠"
    elif cost > 50:
        return "🟡"
    else:
        return "🟢"

def get_cost_explorer_client(region_name='us-east-1'):
    return boto3.client('ce', region_name=region_name)

def get_costs_by_service(ce_client, start_date, end_date):
    response = ce_client.get_cost_and_usage(
        TimePeriod={'Start': start_date, 'End': end_date},
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )
    results = response['ResultsByTime'][0]['Groups']
    return {
        group['Keys'][0]: float(group['Metrics']['UnblendedCost']['Amount'])
        for group in results
    }

def extract_terraform_resources(tfstate_path):
    resource_counts = defaultdict(int)
    instance_types = defaultdict(int)

    try:
        with open(tfstate_path, 'r') as f:
            tfstate = json.load(f)

        for res in tfstate.get('resources', []):
            res_type = res.get('type')
            for instance in res.get('instances', []):
                resource_counts[res_type] += 1
                if res_type == "aws_instance":
                    itype = instance.get('attributes', {}).get('instance_type')
                    if itype:
                        instance_types[itype] += 1
    except Exception:
        pass

    return dict(resource_counts), dict(instance_types)

def summarize_costs(service_costs):
    lines = []
    total = 0.0
    for svc, cost in sorted(service_costs.items(), key=lambda x: -x[1]):
        lines.append(f"{svc:<30} ➤ ${cost:7.2f} {emoji(cost)}")
        total += cost
    return lines, round(total, 2)

def run_check(config):
    test_mode = config.get("test_mode", False)
    region = config.get("aws_region", "us-east-1")
    tfstate_path = config.get("terraform_state")

    if test_mode:
        return AuditResult(
            title="AWS Cost Analysis",
            status=Severity.OK,
            messages=["Test mode enabled. Skipping live AWS billing check."]
        )

    if not tfstate_path or not os.path.exists(tfstate_path):
        return AuditResult(
            title="AWS Cost Analysis",
            status=Severity.CRITICAL,
            messages=["❌ Terraform state file not found."]
        )

    try:
        client = get_cost_explorer_client(region)
        today = datetime.utcnow().replace(day=1)
        start = (today - timedelta(days=1)).replace(day=1)
        end = today

        start_str, end_str = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
        service_costs = get_costs_by_service(client, start_str, end_str)
        resource_counts, ec2_types = extract_terraform_resources(tfstate_path)

        breakdown, total_cost = summarize_costs(service_costs)

        messages = [
            f"🧾 Total cost for last month: ${total_cost:.2f} {emoji(total_cost)}",
            f"📍 AWS Region: {region}",
            f"🔧 Resource Types: {len(resource_counts)}",
            f"🧱 EC2 Instance Types: {', '.join(ec2_types.keys()) or 'N/A'}",
        ]
        messages += [f"• {line}" for line in breakdown[:8]]
        if len(breakdown) > 8:
            messages.append("...")

        # Severity based on bill
        if total_cost > 500:
            severity = Severity.CRITICAL
        elif total_cost > 200:
            severity = Severity.HIGH
        elif total_cost > 50:
            severity = Severity.MEDIUM
        else:
            severity = Severity.OK

        return AuditResult(
            title="AWS Cost Analysis",
            status=severity,
            messages=messages
        )

    except Exception as e:
        return AuditResult(
            title="AWS Cost Analysis",
            status=Severity.CRITICAL,
            messages=[f"❌ Failed to retrieve cost data: {str(e)}"]
        )


