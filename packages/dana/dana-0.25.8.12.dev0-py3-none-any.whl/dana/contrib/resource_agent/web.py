"""Web resource agents & wrappers."""

from collections.abc import Sequence
from dataclasses import dataclass
from functools import cache, cached_property

from llama_index.readers.web.beautiful_soup_web.base import BeautifulSoupWebReader

from dana.common.sys_resource.llm.llm_resource import LLMResource
from dana.util.llm import from_prompts_to_request, from_response_to_content

from .abstract import AbstractResourceAgent

__all__ = ["WebpageResourceAgent", "web_agent"]

@dataclass
class WebpageResourceAgent(AbstractResourceAgent):
    """Webpage resource agent."""

    urls: Sequence[str]

    def __post_init__(self):
        """Post-initialization: parse webpage content and initialize LLM."""
        for url in self.urls:
            assert url.startswith(("http://", "https://")), ValueError(f"{url} doesn't start with http(s)://")

        reader: BeautifulSoupWebReader = BeautifulSoupWebReader(website_extractor=None)

        self.content: list[str] = [doc.text.strip()
                                   for doc in reader.load_data(urls=self.urls,
                                                               custom_hostname=None,
                                                               include_url_in_text=True)]

        self.llm: LLMResource = LLMResource()

    @cached_property
    def system_prompts(self) -> list[str]:
        """System prompts to inject webpage content."""
        return [f"RETAIN THIS WEBPAGE CONTENT IN YOUR KNOWLEDGE:\n"
                f"==============================================\n"
                "\n\n"
                ">>> WEBPAGE CONTENT START >>>\n"
                ">>> ===================== >>>\n"
                "\n\n"
                f"{content}\n"
                "\n\n"
                "^^^ =================== ^^^\n"
                "^^^ WEBPAGE CONTENT END ^^^\n"
                for content in self.content]

    def solve(self, problem: str) -> str:
        """Solve posed problem by leveraging webpage content."""
        return from_response_to_content(self.llm.query_sync(from_prompts_to_request(problem,
                                                                                    system_prompts=self.system_prompts)))  # noqa: E501

@cache
def web_agent(*urls: str) -> WebpageResourceAgent:
    """Create webpage resource agent."""
    return WebpageResourceAgent(urls=urls)
