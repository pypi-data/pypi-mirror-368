"""Agent with multiple resources."""

from functools import cache
from typing import Union

from dana.common.sys_resource.llm.llm_resource import LLMResource

from dana.contrib.resource import as_resource
from dana.contrib.resource.abstract import AbstractResource
from dana.contrib.resource_agent.abstract import AbstractResourceAgent
from dana.util.llm import from_prompts_to_request, from_response_to_content


class MultiAgent(AbstractResourceAgent):
    """Agent with multiple resources."""

    def __init__(self, resources: list[AbstractResource]):
        self.resources = resources
        self.llm = LLMResource(model="openai:gpt-4o-mini")

    def solve(self, problem: str) -> str:
        contexts = "\n\n".join([resource.add_context(problem) for resource in self.resources])
        full_query = f"""{contexts}\n\n{problem}"""
        print(full_query)
        return from_response_to_content(self.llm.query_sync(from_prompts_to_request(full_query)))

@cache
def multi_agent(*resources_or_paths: Union[str, AbstractResource]) -> MultiAgent:
    """Agent with multiple resources.

    Args:
        *resources_or_paths: Either resource paths (str) or pre-configured AbstractResource instances

    Returns:
        MultiAgent instance with the specified resources
    """
    resources = []
    for item in resources_or_paths:
        if isinstance(item, AbstractResource):
            resources.append(item)
        elif isinstance(item, str):
            resources.append(as_resource(item))
        else:
            raise ValueError(f"Expected str or AbstractResource, got {type(item)}")

    return MultiAgent(resources)
