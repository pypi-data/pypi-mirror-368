"""Knowledge Pack resource agent & wrapper."""

from dataclasses import dataclass
from functools import cache, cached_property

from dana.common.sys_resource.llm.llm_resource import LLMResource

from dana.util.llm import from_prompts_to_request, from_response_to_content

from dana.contrib.knows import Kpk
from dana.contrib.knows.core.fs import PathOrStr

from .abstract import AbstractResourceAgent

__all__ = ["KpkResourceAgent", "kpk_agent"]

@dataclass
class KpkResourceAgent(AbstractResourceAgent):
    """Knowledge Pack resource agent."""

    path: PathOrStr

    def __post_init__(self):
        """Post-initialization: initialize & organize the Knowledge Pack and initialize LLM."""
        self.kpk: Kpk = Kpk(path=self.path)

        self.llm: LLMResource = LLMResource()

    @cached_property
    def system_prompts(self) -> list[str]:
        """System prompts to inject Expert Text Notes from the Knowledge Pack."""
        return [f"RETAIN THIS EXPERT TEXT NOTE IN YOUR KNOWLEDGE:\n"
                f"===============================================\n"
                "\n\n"
                ">>> EXPERT TEXT NOTE START >>>\n"
                ">>> ====================== >>>\n"
                "\n\n"
                f"{expert_text_note.content}\n"
                "\n\n"
                "^^^ ==================== ^^^\n"
                "^^^ EXPERT TEXT NOTE END ^^^\n"
                for expert_text_note in self.kpk.expert_text_notes]

    def solve(self, problem: str, quick: bool = False) -> str:
        """Solve a problem using the Knowledge Pack."""
        # TODO: make more comprehensive
        if quick:
            return self.kpk.retrieve(query=problem)

        assert self.kpk.expert_text_notes, ValueError("Expert Text Notes needed for thorough problem solving.")

        return from_response_to_content(self.llm.query_sync(from_prompts_to_request(problem,
                                                                                    system_prompts=self.system_prompts)))  # noqa: E501

@cache
def kpk_agent(kpk_path: str) -> KpkResourceAgent:
    """Create Knowledge Pack resource agent."""
    return KpkResourceAgent(path=kpk_path)
