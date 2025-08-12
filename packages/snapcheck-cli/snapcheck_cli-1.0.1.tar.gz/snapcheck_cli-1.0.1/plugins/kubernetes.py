import datetime
import os
from kubernetes import client, config
from kubernetes.stream import stream
from utils.reporter import AuditResult, Severity


def run_check(config_data):
    test_mode = config_data.get("test_mode", False)
    diagnostics = []

    if test_mode:
        return AuditResult(
            title="Kubernetes Cluster Audit",
            status=Severity.OK,
            messages=["Test mode enabled. Skipping live cluster diagnostics."]
        )

    try:
        config.load_kube_config(config_file=config_data.get("kubeconfig"))
    except Exception as e:
        return AuditResult(
            title="Kubernetes Cluster Audit",
            status=Severity.CRITICAL,
            messages=[f"❌ Failed to connect to cluster: {e}"]
        )

    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    messages = []
    severity = Severity.OK

    # Node Readiness & Pressure
    unready_nodes = []
    pressure_nodes = []
    for node in v1.list_node().items:
        for condition in node.status.conditions:
            if condition.type == "Ready" and condition.status != "True":
                unready_nodes.append(node.metadata.name)
            if condition.type in ["MemoryPressure", "DiskPressure"] and condition.status == "True":
                pressure_nodes.append(f"{node.metadata.name} - {condition.type}")

    if unready_nodes:
        messages.append(f"🚨 Unready nodes: {', '.join(unready_nodes)}")
        severity = Severity.HIGH
    if pressure_nodes:
        messages.append(f"⚠️ Node pressure detected: {', '.join(pressure_nodes)}")
        if severity == Severity.OK:
            severity = Severity.MEDIUM

    # Pod status
    crashloop_pods = []
    restarted_pods = []
    failed_liveness = []
    for pod in v1.list_pod_for_all_namespaces().items:
        for status in pod.status.container_statuses or []:
            if status.state.waiting and status.state.waiting.reason == "CrashLoopBackOff":
                crashloop_pods.append(f"{pod.metadata.namespace}/{pod.metadata.name}")
            if status.restart_count and status.restart_count > 3:
                restarted_pods.append(f"{pod.metadata.namespace}/{pod.metadata.name} - restarts: {status.restart_count}")
            if status.ready is False and not status.state.running:
                failed_liveness.append(f"{pod.metadata.namespace}/{pod.metadata.name}")

    if crashloop_pods:
        messages.append(f"❌ CrashLoopBackOff pods: {', '.join(crashloop_pods)}")
        severity = Severity.HIGH
    if restarted_pods:
        messages.append(f"♻️ High pod restarts: {', '.join(restarted_pods)}")
        if severity == Severity.OK:
            severity = Severity.MEDIUM
    if failed_liveness:
        messages.append(f"🔍 Readiness/Liveness failures: {', '.join(failed_liveness)}")
        if severity == Severity.OK:
            severity = Severity.MEDIUM

    # PVC status
    pvc_issues = []
    for pvc in v1.list_persistent_volume_claim_for_all_namespaces().items:
        if pvc.status.phase != "Bound":
            pvc_issues.append(f"{pvc.metadata.namespace}/{pvc.metadata.name} - {pvc.status.phase}")
    if pvc_issues:
        messages.append(f"💾 Unbound PVCs: {', '.join(pvc_issues)}")
        if severity == Severity.OK:
            severity = Severity.MEDIUM

    # DNS test (nslookup)
    try:
        pods = v1.list_namespaced_pod(namespace="kube-system").items
        if pods:
            test_pod = pods[0].metadata.name
            output = stream(v1.connect_get_namespaced_pod_exec, test_pod, "kube-system",
                            command=["nslookup", "kubernetes.default"], stderr=True, stdin=False, stdout=True, tty=False)
            if "can't find" in output.lower():
                messages.append("❌ DNS resolution failed inside pod")
                severity = Severity.HIGH
    except Exception as e:
        messages.append(f"⚠️ DNS test failed to execute: {e}")
        if severity == Severity.OK:
            severity = Severity.MEDIUM

    # Services with no endpoints
    no_endpoints = []
    for ep in v1.list_endpoints_for_all_namespaces().items:
        if not ep.subsets:
            no_endpoints.append(f"{ep.metadata.namespace}/{ep.metadata.name}")
    if no_endpoints:
        messages.append(f"🔌 Services with no endpoints: {', '.join(no_endpoints)}")
        if severity == Severity.OK:
            severity = Severity.MEDIUM

    # Security Checks
    privileged_containers = []
    hostpath_volumes = []
    for pod in v1.list_pod_for_all_namespaces().items:
        for container in pod.spec.containers:
            if container.security_context and container.security_context.privileged:
                privileged_containers.append(f"{pod.metadata.namespace}/{pod.metadata.name}")
        for vol in pod.spec.volumes or []:
            if vol.host_path:
                hostpath_volumes.append(f"{pod.metadata.namespace}/{pod.metadata.name} uses hostPath")
    if privileged_containers:
        messages.append(f"🔐 Privileged containers found: {', '.join(privileged_containers)}")
        severity = Severity.HIGH
    if hostpath_volumes:
        messages.append(f"⚠️ HostPath volumes detected: {', '.join(hostpath_volumes)}")
        if severity == Severity.OK:
            severity = Severity.MEDIUM

    if not messages:
        messages.append("✅ All checks passed. Cluster looks healthy.")

    return AuditResult(
        title="Kubernetes Cluster Audit",
        status=severity,
        messages=messages
    )


