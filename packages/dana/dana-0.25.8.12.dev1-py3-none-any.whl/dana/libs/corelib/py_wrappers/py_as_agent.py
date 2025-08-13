"""
Resource Agent Function for Dana Standard Library

This module provides the as_agent function that intelligently determines resource type
and creates appropriate agent wrappers for solving problems with various resources.

Copyright © 2025 Aitomatic, Inc.
MIT License
"""

from typing import Literal, Optional

from dana.core.lang.sandbox_context import SandboxContext
from dana.contrib.resource_agent import as_agent

__all__ = ["py_as_agent"]

def py_as_agent(context: SandboxContext,
                *resource_paths: str,
                type: Optional[Literal["csv", "db", "doc", "kpk", "mcp", "web"]] = None):
    """
    Intelligently determine resource type and use the appropriate wrapper.
    If type is specified, use that wrapper directly.
    Otherwise, try to infer the type from the resource path.

    Args:
        context: The sandbox context
        resource_paths: Paths or URLs to the resources
        type: Optional resource type ('csv', 'db', 'doc', 'kpk', 'mcp', 'web')

    Returns:
        Resource-using agent instance with .solve() method

    Examples:
        >>> agent = as_agent('path/to/file1.pdf', 'path/to/file2.pdf')  # Uses doc wrapper
        >>> agent = as_agent('data.csv')  # Uses csv wrapper
        >>> agent = as_agent('https://example.com')  # Uses web wrapper
        >>> agent = as_agent('postgresql://user:pass@host/db')  # Uses db wrapper
        >>> agent = as_agent('path/to/file', type='doc')  # Forces doc wrapper
        >>> agent = as_agent('path/to/dir', type='kpk')  # Uses kpk wrapper
        >>> agent = as_agent('https://example.com', type='mcp')  # Uses mcp wrapper

        # Use the agent to solve problems
        >>> result = agent.solve("What is the main topic of this document?")
        >>> result = agent.solve("Analyze the data and provide insights")
    """
    return as_agent(*resource_paths, type=type)
