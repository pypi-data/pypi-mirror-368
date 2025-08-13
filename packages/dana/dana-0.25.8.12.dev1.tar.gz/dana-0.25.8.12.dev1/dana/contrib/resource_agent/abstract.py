"""Abstract Resource-Using Agent."""

from abc import ABC, abstractmethod
from typing import Any

class AbstractResourceAgent(ABC):
    """Abstract Resource-Using Agent."""

    @property
    def system_prompts(self) -> list[str]:
        """System prompts."""
        return []

    @abstractmethod
    def solve(self, problem: str, **kwargs: Any) -> str:
        """Solve posed problem using underlying resource."""
