"""Dana built-in `solve(...)` function."""

from dana.common.sys_resource.llm.llm_resource import LLMResource
from dana.util.llm import from_prompts_to_request, from_response_to_content

def solve(problem: str) -> str:
    """Solve a problem using the Dana built-in `solve(...)` function."""
    return from_response_to_content(LLMResource().query_sync(from_prompts_to_request(problem)))
