<div style="display: flex; justify-content: center; align-items: center;">
  <img
    src="https://docs.arcade.dev/images/logo/arcade-logo.png"
    style="width: 250px;"
  >
</div>

<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px;">
  <img src="https://img.shields.io/github/v/release/tushar-rishav/arcade_k8s" alt="GitHub release" style="margin: 0 2px;">
  <img src="https://img.shields.io/badge/python-3.13+-blue.svg" alt="Python version" style="margin: 0 2px;">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License" style="margin: 0 2px;">
  <img src="https://img.shields.io/pypi/v/arcade_k8s" alt="PyPI version" style="margin: 0 2px;">
</div>
<div style="display: flex; justify-content: center; align-items: center;">
  <a href="https://github.com/tushar-rishav/arcade_k8s" target="_blank">
    <img src="https://img.shields.io/github/stars/tushar-rishav/arcade_k8s" alt="GitHub stars" style="margin: 0 2px;">
  </a>
  <a href="https://github.com/tushar-rishav/arcade_k8s/fork" target="_blank">
    <img src="https://img.shields.io/github/forks/tushar-rishav/arcade_k8s" alt="GitHub forks" style="margin: 0 2px;">
  </a>
</div>


<br>
<br>

# Arcade k8s Toolkit
List resource utilization for kubernetes nodes and pods
## Features

#### top_nodes
List resource utilization for kubernetes nodes

#### top_pods
List pods utilization for kubernetes pods

## Usage
```python
import os
from arcadepy import Arcade
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    arcade_api_key = os.getenv("API_KEY")
    arcade_user_id = os.getenv("USER_ID")

    client = Arcade(api_key=arcade_api_key)
    user_id = arcade_user_id

    result_nodes = client.tools.execute(
      tool_name="arcade_k8s.TopNodes@0.1.0",
      user_id=user_id,
    )
    result_pods = client.tools.execute(
      tool_name="arcade_k8s.TopPods@0.1.0",
      user_id=user_id,
      input={
            "namespace": "default"
      },
    )

print(result_nodes, result_pods)
```

## Development

Read the docs on how to create a toolkit [here](https://docs.arcade.dev/home/build-tools/create-a-toolkit)