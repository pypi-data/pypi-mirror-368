from pathlib import Path

from llama_index.core import VectorStoreIndex
from llama_index.readers.file.paged_csv import PagedCSVReader

from dana.contrib.resource.abstract import AbstractResource


class CSVResource(AbstractResource):
    """CSV resource."""

    def __init__(self, path: str | Path, guidance: str | None = None, top_k: int = 20):
        """Initialize CSV resource.

        Args:
            path: Path to the CSV file.
            guidance: Guidance for how to interpret the CSV data that follows.
            top_k: Number of top results to retrieve.
        """
        self.path = Path(path).resolve()
        self.guidance = guidance or f"CSV data from {self.path.name}:"
        self.top_k = top_k

        # Initialize retriever
        docs = PagedCSVReader().load_data(file=self.path)
        index = VectorStoreIndex.from_documents(docs)
        self.retriever = index.as_retriever(similarity_top_k=self.top_k)

    def add_context(self, problem: str) -> str:
        """Retrieve relevant data from the CSV file."""
        nodes = self.retriever.retrieve(problem)
        csv_data = "\n\n".join(n.node.get_content(metadata_mode="llm") for n in nodes)
        return f"{self.guidance}\n\n{csv_data}"
