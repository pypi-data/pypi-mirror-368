from typing import Annotated


from kubernetes import client, config
from arcade_tdk import tool


@tool
def top_nodes() -> str:
    """List top nodes in Kubernetes with resource utilization!"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        nodes = v1.list_node().items
        nodes_sorted = sorted(nodes, key=lambda n: n.metadata.creation_timestamp)

        # Try to get node metrics from metrics.k8s.io API
        try:
            metrics_client = client.CustomObjectsApi()
            node_metrics = metrics_client.list_cluster_custom_object(
                group="metrics.k8s.io", version="v1beta1", plural="nodes"
            )
            metrics_map = {item['metadata']['name']: item for item in node_metrics.get('items', [])}
        except Exception:
            metrics_map = {}

        output_lines = ["NAME\tADDRESS\tSTATUS\tCPU(usage)\tMEMORY(usage)"]
        for n in nodes_sorted:
            name = n.metadata.name
            address = n.status.addresses[0].address
            status = f"{n.status.conditions[-1].type}:{n.status.conditions[-1].status}"
            cpu = mem = "N/A"
            if name in metrics_map:
                usage = metrics_map[name]["usage"]
                cpu = usage.get("cpu", "N/A")
                mem = usage.get("memory", "N/A")
            output_lines.append(f"{name}\t{address}\t{status}\t{cpu}\t{mem}")
        return "\n".join(output_lines)
    except Exception as e:
        return f"Error listing top nodes: {e}"


