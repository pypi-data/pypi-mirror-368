from abc import ABC, abstractmethod


class AbstractResource(ABC):
    """Abstract resource."""

    @abstractmethod
    def add_context(self, problem: str) -> str:
        """Provide additional context to the problem prompt."""
