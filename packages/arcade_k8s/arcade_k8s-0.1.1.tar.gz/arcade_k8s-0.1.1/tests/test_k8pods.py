from arcade_k8s.tools.pods import top_pods

def test_top_pods_runs() -> None:
    # Use 'default' namespace for a basic test; adjust as needed
    result = top_pods("default")
    assert isinstance(result, str)
    assert "NAME" in result and "CPU" in result and "MEMORY" in result
