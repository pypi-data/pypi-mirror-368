"""MCP resource agent & wrapper."""

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
from functools import cache
import json
from pprint import pformat
from typing import Any, TypedDict

from mcp.client.streamable_http import streamablehttp_client

from loguru import logger

from dana.contrib.solve import solve as built_in_solve

from .abstract import AbstractResourceAgent

__all__ = ["McpAgent", "mcp_agent"]

type McpResourceRead = str

class McpToolCall(TypedDict):
    name: str
    arguments: dict[str, Any]

type McpPlan = Sequence[dict[str, set[McpResourceRead] | set[McpToolCall]]]

# TODO: update to use MCP library instead of FastMCP

@dataclass
class McpAgent(AbstractResourceAgent):
    """MCP resource agent."""

    server_url: str

    def __post_init__(self):
        """Post-initialization: validate the MCP server URL."""
        self.client = streamablehttp_client(url=self.server_url,
                                            headers=None,
                                            timeout=30,
                                            sse_read_timeout=60 * 5,
                                            terminate_on_close=True,
                                            # httpx_client_factory=
                                            auth=None)

        asyncio.run(self.inspect_server())

    async def inspect_server(self):
        """Inspect prompts, resources and tools available on the MCP server."""
        async with self.client:
            self.prompts, self.resources, self.resource_templates, self.tools = \
                await asyncio.gather(self.client.list_prompts(),
                                     self.client.list_resources(),
                                     self.client.list_resource_templates(),
                                     self.client.list_tools(),
                                     return_exceptions=True)

            logger.debug(f"{self.server_url} MCP Prompts:\n\n{pformat(self.prompts, indent=2)}\n")
            logger.debug(f"{self.server_url} MCP Resources:\n\n{pformat(self.resources, indent=2)}\n")
            logger.debug(f"{self.server_url} MCP Resource templates:\n\n{pformat(self.resource_templates, indent=2)}\n")
            logger.debug(f"{self.server_url} MCP Tools:\n\n{pformat(self.tools, indent=2)}\n")

    def plan(self, problem: str) -> McpPlan:
        """Plan the sequence of parallizable sets of MCP resource readings and tool calls to solve the problem."""

        planning_prompt: str = (f"""
            Given that you have access to the following MCP resources and tools:

            RESOURCES:
            ```
            {'\n\n'.join(str(resource) for resource in self.resources)}
            ```

            TOOLS:
            ```
            {'\n\n'.join(str(tool) for tool in self.tools)}
            ```

            Give me a SEQUENCE of PARALLELIZABLE SETS of MCP resource readings and tool calls
            most likely to solve this problem:

            PROBLEM:
            ```
            {problem}
            ```

            Return your plan in a JSON LIST string of the following format:
            ```
            [
                {{
                    "PARALLEL-RESOURCE-READS": [
                        "resource_uri_1",
                        "resource_uri_2",
                        ...
                    ],

                    "PARALLEL-TOOL-CALLS": [
                        {{
                            "name": "tool_name_a",
                            "arguments": {{
                                "arg_name_a1": "arg_value_a1",
                                "arg_name_a2": "arg_value_a2",
                                ...
                            }},
                        }},
                        {{
                            "name": "tool_name_b",
                            "arguments": {{
                                "arg_name_b1": "arg_value_b1",
                                "arg_name_b2": "arg_value_b2",
                                ...
                            }},
                        }},
                        ...
                    ],
                }},

                {{
                    "PARALLEL-RESOURCE-READS": [
                        "resource_uri_3",
                        "resource_uri_4",
                        ...
                    ],

                    "PARALLEL-TOOL-CALLS": [
                        {{
                            "name": "tool_name_c",
                            "arguments": {{
                                "arg_name_c1": "arg_value_c1",
                                "arg_name_c2": "arg_value_c2",
                                ...
                            }},
                        }},
                        {{
                            "name": "tool_name_d",
                            "arguments": {{
                                "arg_name_d1": "arg_value_d1",
                                "arg_name_d2": "arg_value_d2",
                                ...
                            }},
                        }},
                        ...
                    ],
                }},
                ...
            ]
            ```

            NOTE: Return ONLY the JSON LIST, and NOTHING ELSE / NO OTHER TEXT,
            NOT EVEN surrounding quotation characters such as the "```" wrapping!
        """)

        type TempMcpPlan = list[dict[str, list[McpResourceRead] | list[McpToolCall]]]

        plan: TempMcpPlan = []

        def validate_plan(plan: TempMcpPlan) -> bool:
            """Validate a parsed plan."""
            if not plan:
                return False

            if not isinstance(plan, list):
                return False

            for step in plan:
                if not isinstance(step, dict):
                    return False

                if 'PARALLEL-RESOURCE-READS' not in step:
                    return False
                if not isinstance(parallel_resource_reads := step['PARALLEL-RESOURCE-READS'], list):
                    return False
                if parallel_resource_reads and any(not isinstance(uri, str) for uri in parallel_resource_reads):
                    return False

                if 'PARALLEL-TOOL-CALLS' not in step:
                    return False

                if not isinstance(parallel_tool_calls := step['PARALLEL-TOOL-CALLS'], list):
                    return False

                for parallel_tool_call in parallel_tool_calls:
                    if not isinstance(parallel_tool_call, dict):
                        return False

                    if 'name' not in parallel_tool_call:
                        return False
                    if not isinstance(_ := parallel_tool_call['name'], str):
                        return False

                    if 'arguments' not in parallel_tool_call:
                        return False
                    if not isinstance(_ := parallel_tool_call['arguments'], dict):
                        return False

            return True

        while not validate_plan(plan):
            if plan:
                logger.warning(f"Invalid plan:\n\n{pformat(plan, indent=2, sort_dicts=False)}\n")

            plan_str = built_in_solve(problem=planning_prompt)

            try:
                plan = json.loads(plan_str)
            except json.JSONDecodeError:
                logger.error(f"JSON-unparseable plan:\n\n{plan_str}\n")

        logger.debug(f"{self.server_url} MCP Plan:\n\n{pformat(plan, indent=2, sort_dicts=False)}\n")

        return plan

    async def execute_plan(self, plan: McpPlan) -> list[dict[str, dict[str, Any]]]:
        """Execute a MCP plan."""
        plan_outputs: list[dict[str, dict[str, Any]]] = []

        for step in plan:
            async with self.client:
                step_outputs = await asyncio.gather(*(self.client.read_resource(uri=resource_read_uri)
                                                      for resource_read_uri in step['PARALLEL-RESOURCE-READS']),

                                                    *(self.client.call_tool(name=tool_call['name'],
                                                                            arguments=tool_call['arguments'],
                                                                            timeout=None,
                                                                            progress_handler=None)
                                                      for tool_call in step['PARALLEL-TOOL-CALLS']),

                                                    return_exceptions=True)

                step_outputs_presentation: dict[str, Any] = {}

                step_outputs_presentation['RESOURCE-READS'] = {}
                for resource_read_uri in step['PARALLEL-RESOURCE-READS']:
                    step_outputs_presentation['RESOURCE-READS'][resource_read_uri] = step_outputs.pop(0)

                step_outputs_presentation['TOOL-CALLS'] = {}
                for tool_call in step['PARALLEL-TOOL-CALLS']:
                    step_outputs_presentation['TOOL-CALLS'][tool_call['name']] = step_outputs.pop(0)

                plan_outputs.append(step_outputs_presentation)

        return plan_outputs

    async def async_solve(self, problem: str) -> str:
        """Solve posed problem using MCP resources & tools."""

        plan: McpPlan = self.plan(problem)

        plan_outputs = await self.execute_plan(plan)

        return built_in_solve(f"""
            Given the following MCP outputs:

            MCP OUTPUTS:
            ```
            {pformat(plan_outputs, indent=2, sort_dicts=False)}
            ```

            Provide your best answer/solution to the following problem:

            PROBLEM:
            ```
            {problem}
            ```
            """)

    def solve(self, problem: str) -> str:
        """Solve posed problem using MCP resources & tools."""
        return asyncio.run(self.async_solve(problem))

@cache
def mcp_agent(mcp_server_url: str) -> McpAgent:
    """Create an MCP resource agent."""
    return McpAgent(mcp_server_url)
