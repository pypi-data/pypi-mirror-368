from functools import cache

from .abstract import AbstractResource
from .csv import CSVResource

__all__ = ["as_resource"]

@cache
def as_resource(resource_path: str, **kwargs) -> AbstractResource:
    """Create a resource from a path.

    Args:
        resource_path: Path to the resource file
        **kwargs: Additional configuration parameters for the resource

    Returns:
        Configured AbstractResource instance

    Raises:
        ValueError: If the resource type is not supported
    """
    if resource_path.endswith(".csv"):
        return CSVResource(resource_path, **kwargs)
    else:
        raise ValueError(f"Unsupported resource type: {resource_path}")
