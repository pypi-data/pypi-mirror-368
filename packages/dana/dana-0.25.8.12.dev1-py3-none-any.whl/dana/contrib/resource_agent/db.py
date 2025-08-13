"""Database resource agent & wrapper."""

from dataclasses import dataclass
from functools import cache

from .abstract import AbstractResourceAgent

__all__ = ["DbResourceAgent", "db_agent"]

@dataclass
class DbResourceAgent(AbstractResourceAgent):
    """Database resource agent."""

    db_connection: str

    def solve(self, problem: str) -> str:
        """TODO: Solve posed problem using database resource."""

@cache
def db_agent(db_connection: str) -> DbResourceAgent:
    """Create database resource agent."""
    return DbResourceAgent(db_connection=db_connection)
