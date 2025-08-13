"""Resource agent wrapper."""

from functools import cache
from pathlib import Path
from typing import Literal, Optional, Union
from urllib.parse import urlparse

from dana.contrib.resource.abstract import AbstractResource

from .abstract import AbstractResourceAgent
from .csv import csv_agent
from .db import db_agent
from .doc import doc_agent
from .kpk import kpk_agent
from .mcp import mcp_agent
from .multi import multi_agent
from .web import web_agent

__all__ = ["as_agent", "as_multi_agent"]

@cache
def as_agent(*resource_paths: str,
             type: Optional[Literal["csv", "db", "doc", "kpk", "mcp", "web"]] = None) -> AbstractResourceAgent:
    """
    Intelligently determine resource type and use the appropriate wrapper.
    If type is specified, use that wrapper directly.
    Otherwise, try to infer the type from the resource path.

    Args:
        resource_paths: Paths or URLs to the resources
        type: Optional resource type ('csv', 'db', 'doc', 'kpk', 'mcp', 'web')

    Returns:
        Resource-using agent instance

    Examples:
        >>> as_agent('path/to/file1.pdf', 'path/to/file2.pdf')  # Uses doc wrapper
        >>> as_agent('data.csv')  # Uses csv wrapper
        >>> as_agent('https://example.com')  # Uses web wrapper
        >>> as_agent('https://example1.com', 'https://example2.com')  # Uses web wrapper with multiple URLs
        >>> as_agent('postgresql://user:pass@host/db')  # Uses db wrapper
        >>> as_agent('path/to/file', type='doc')  # Forces doc wrapper
        >>> as_agent('path/to/dir', type='kpk')  # Uses kpk wrapper
        >>> as_agent('https://example.com', type='mcp')  # Uses mcp wrapper
        >>> as_agent('data.csv', type='csv')  # Forces csv wrapper
    """
    if not resource_paths:
        raise ValueError("At least one resource path must be provided")

    # Handle single path case
    if len(resource_paths) == 1:
        resource_path = resource_paths[0]
        parsed = urlparse(resource_path)

        # Handle URLs
        if parsed.scheme:
            if parsed.scheme in ('http', 'https'):
                if type == 'mcp':
                    return mcp_agent(resource_path)

                elif type and type != 'web':
                    raise ValueError(f"Type mismatch: URL {resource_path} requires type 'web' or 'mcp', got '{type}'")

                return web_agent(resource_path)

            elif parsed.scheme in ('postgresql', 'mysql', 'sqlite'):
                if type and type != 'db':
                    raise ValueError(f"Type mismatch: URL {resource_path} requires type 'db', got '{type}'")

                return db_agent(resource_path)

        # Handle CSV files
        if type == 'csv' or (not type and Path(resource_path).suffix.lower() == '.csv'):
            return csv_agent(resource_path)

        # Handle kpk type (must be a single local path)
        elif type == 'kpk':
            return kpk_agent(resource_path)

        # Handle single document path
        else:
            return doc_agent(resource_path)

    # Handle CSV type validation
    if type == 'csv':
        if len(resource_paths) != 1:
            raise ValueError("CSV wrapper requires exactly 1 resource path")
        return csv_agent(resource_paths[0])

    # Handle kpk type validation
    if type in ('db', 'kpk', 'mcp'):
        raise ValueError(f"'{type}' wrapper requires exactly 1 resource path")

    # Handle multiple paths case
    if len(resource_paths) > 1:
        # Check if all paths are valid URLs
        all_urls = True
        urls = []
        for resource_path in resource_paths:
            parsed = urlparse(resource_path)
            if not parsed.scheme or parsed.scheme not in ('http', 'https'):
                all_urls = False
                break
            urls.append(resource_path)

        if all_urls:
            # Multiple URLs case
            if type and type != 'web':
                raise ValueError(f"Type mismatch: Multiple URLs require type 'web', got '{type}'")

            return web_agent(*urls)

        else:
            # Multiple documents case
            if type and type != 'doc':
                raise ValueError(f"Type mismatch: Multiple local paths require type 'doc', got '{type}'")

            if any(urlparse(str(resource_path)).scheme for resource_path in resource_paths):
                raise ValueError("Document wrapper cannot handle URLs")

            return doc_agent(*resource_paths)

    raise ValueError(f"Unknown or invalid resource specifications: {resource_paths} with type {type}")

@cache
def as_multi_agent(*resources_or_paths: Union[str, AbstractResource]) -> AbstractResourceAgent:
    """Agent with multiple resources.

    Args:
        *resources_or_paths: Either resource paths (str) or pre-configured AbstractResource instances
        type: Optional resource type (currently only supports "csv")

    Returns:
        MultiAgent instance with the specified resources
    """
    return multi_agent(*resources_or_paths)
