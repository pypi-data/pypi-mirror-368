from arcade_tdk import ToolCatalog
from arcade_evals import (
    EvalRubric,
    EvalSuite,
    ExpectedToolCall,
    tool_eval,
)
from arcade_evals.critic import SimilarityCritic

import arcade_k8s
from arcade_k8s.tools.nodes import top_nodes
from arcade_k8s.tools.pods import top_pods

# Evaluation rubric
rubric = EvalRubric(
    fail_threshold=0.85,
    warn_threshold=0.95,
)


catalog = ToolCatalog()
catalog.add_module(arcade_k8s)


@tool_eval()
def k8nodes_eval_suite() -> EvalSuite:
    suite = EvalSuite(
        name="k8nodes Tools Evaluation",
        system_message=(
            "You are an AI assistant with access to k8nodes tools. "
            "Use them to help the user with their tasks."
        ),
        catalog=catalog,
        rubric=rubric,
    )


    suite.add_case(
        name="Listing top nodes",
        user_message="What are the top nodes in my Kubernetes cluster?",
        expected_tool_calls=[ExpectedToolCall(func=top_nodes)],
        rubric=rubric,
        critics=[
            SimilarityCritic(critic_field="name", weight=0.5),
        ],
        additional_messages=[
            {"role": "user", "content": "My friend's name is John Doe."},
            {"role": "assistant", "content": "It is great that you have a friend named John Doe!"},
        ],
    )

    suite.add_case(
        name="Listing top pods",
        user_message="What are the top pods in the default namespace?",
        expected_tool_calls=[ExpectedToolCall(func=top_pods, args=["default"])],
        rubric=rubric,
        critics=[
            SimilarityCritic(critic_field="name", weight=0.5),
        ],
    )

    return suite
