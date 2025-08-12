from arcade_k8s.tools.nodes import top_nodes

def test_top_nodes_runs() -> None:
    result = top_nodes()
    assert isinstance(result, str)
    assert "NAME" in result and "CPU" in result and "MEMORY" in result