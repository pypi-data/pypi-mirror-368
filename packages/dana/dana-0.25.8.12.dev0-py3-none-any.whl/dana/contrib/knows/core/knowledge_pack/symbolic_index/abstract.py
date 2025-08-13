"""Abstract Symbolic Indexer, Index and Retriever."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cache
from typing import ClassVar

from dana.contrib.knows.core.fs import PathOrStr

__all__ = [
    "AbstractSymbolicIndexer",
    "AbstractSymbolicIndex",
    "AbstractSymbolicRetriever",
]

@dataclass
class AbstractSymbolicIndexer(ABC):
    """Abstract Symbolic Indexer."""

    INDEX_CLASS: ClassVar[type[AbstractSymbolicIndex]]

    docs_dir_path: PathOrStr

    @abstractmethod
    def persist_index(self, persist_dir_path: PathOrStr, force: bool = False):
        """Persist symbolic/structured relationships from documents into symbolic index."""

@dataclass
class AbstractSymbolicIndex(ABC):
    """Abstract Symbolic Index."""

    IMPLEMENTATION_NAME: ClassVar[str]

    RETRIEVER_CLASS: ClassVar[type[AbstractSymbolicRetriever]]

    persist_dir_path: PathOrStr

    @cache
    def retriever(self, **kwargs) -> AbstractSymbolicRetriever:
        """Get symbolic retriever."""
        return self.RETRIEVER_CLASS(symbolic_index=self, **kwargs)

@dataclass
class AbstractSymbolicRetriever(ABC):
    """Abstract Symbolic Retriever."""

    symbolic_index: AbstractSymbolicIndex

    @abstractmethod
    def retrieve(self, query: str) -> str:
        """Retrieve relevant information from symbolic index and synthesize response to query."""
