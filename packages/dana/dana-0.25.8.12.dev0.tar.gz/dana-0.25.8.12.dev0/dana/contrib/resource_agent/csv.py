"""CSV resource agent & wrapper."""

from dataclasses import dataclass
from functools import cache
from pathlib import Path

from llama_index.core import VectorStoreIndex
from llama_index.readers.file.paged_csv import PagedCSVReader
from dana.common.sys_resource.llm.llm_resource import LLMResource

from dana.util.llm import from_prompts_to_request, from_response_to_content

from .abstract import AbstractResourceAgent

__all__ = ["CsvResourceAgent", "csv_agent"]

@dataclass
class CsvResourceAgent(AbstractResourceAgent):
    """CSV resource agent that treats each line as a document."""

    path: str | Path

    def __post_init__(self):
        """Post-initialization: validate CSV file and initialize LLM."""
        # Persist to same dir as CSV file under /storage.
        persist_dir = Path(self.path).parent / "storage"
        docs = PagedCSVReader().load_data(file=self.path)
        index = VectorStoreIndex.from_documents(docs)
        index.storage_context.persist(persist_dir=persist_dir)
        self.retriever = index.as_retriever(similarity_top_k=20)
        self.llm: LLMResource = LLMResource(model="openai:gpt-4o-mini")

    def solve(self, problem: str) -> str:
        """Solve posed problem by leveraging CSV content."""
        # Simple RAG lookup
        nodes = self.retriever.retrieve(problem)
        csv_data = "\n\n".join(n.node.get_content(metadata_mode="llm") for n in nodes)
        enhanced_prompt = f"{problem}\n\nRelevant CSV data:\n{csv_data}\n\nUse this data to answer the question."

        print(enhanced_prompt)
        return from_response_to_content(self.llm.query_sync(from_prompts_to_request(enhanced_prompt)))

@cache
def csv_agent(path: str | Path) -> CsvResourceAgent:
    """Create CSV resource agent."""
    return CsvResourceAgent(path=path)
