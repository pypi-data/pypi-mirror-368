"""KNOWS miscellaneous utilities."""

from __future__ import annotations

from functools import cache
from importlib import import_module

__all__ = ["class_from_string"]

@cache
def class_from_string(class_path: str, /) -> type:
    """Get a class from a string."""
    module_name, class_name = class_path.rsplit(".", 1)
    module = import_module(module_name)
    return getattr(module, class_name)
