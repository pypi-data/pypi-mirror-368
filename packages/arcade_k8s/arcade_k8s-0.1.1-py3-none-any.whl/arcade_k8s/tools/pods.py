from typing import Annotated


from kubernetes import client, config
from arcade_tdk import tool

@tool
def top_pods(namespace: Annotated[str, "The Kubernetes namespace to query"]) -> str:
    """List top pods in a given Kubernetes namespace with resource utilization."""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace=namespace).items
        pods_sorted = sorted(pods, key=lambda p: p.metadata.creation_timestamp)

        # Try to get pod metrics from metrics.k8s.io API
        try:
            metrics_client = client.CustomObjectsApi()
            pod_metrics = metrics_client.list_namespaced_custom_object(
                group="metrics.k8s.io", version="v1beta1", namespace=namespace, plural="pods"
            )
            pod_metrics_map = {item['metadata']['name']: item for item in pod_metrics.get('items', [])}
        except Exception:
            pod_metrics_map = {}

        output_lines = ["NAME\tPHASE\tCREATED\tCPU(usage)\tMEMORY(usage)"]
        for p in pods_sorted:
            name = p.metadata.name
            phase = p.status.phase
            created = p.metadata.creation_timestamp
            cpu = mem = "N/A"
            if name in pod_metrics_map:
                containers = pod_metrics_map[name].get("containers", [])
                cpu_sum = mem_sum = ""
                cpu_list = [c["usage"].get("cpu", "0") for c in containers]
                mem_list = [c["usage"].get("memory", "0") for c in containers]
                cpu = ",".join(cpu_list) if cpu_list else "N/A"
                mem = ",".join(mem_list) if mem_list else "N/A"
            output_lines.append(f"{name}\t{phase}\t{created}\t{cpu}\t{mem}")
        return "\n".join(output_lines)
    except Exception as e:
        return f"Error listing top pods in namespace '{namespace}': {e}"