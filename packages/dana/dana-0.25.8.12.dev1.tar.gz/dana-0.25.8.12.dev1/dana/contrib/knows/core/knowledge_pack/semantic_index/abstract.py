"""Abstract Semantic Indexer, Index and RAG."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Any, ClassVar, Optional

import yaml

from dana.contrib.knows.core.fs import Dir, PathOrStr
from dana.contrib.knows.util.misc import class_from_string

__all__ = [
    "AbstractSemanticIndexer",
    "AbstractSemanticIndex",
    "AbstractSemanticRAG",
]

INDEXER_PARAMS_FILE_NAME: str = "INDEXER-PARAMS.yml"
EMBED_MODEL_CLASS_KEY: str = "EMBED-MODEL-CLASS"
EMBED_MODEL_NAME_KEY: str = "EMBED-MODEL-NAME"
EMBED_MODEL_ARGS_KEY: str = "EMBED-MODEL-ARGS"

@dataclass
class AbstractSemanticIndexer(ABC):
    """Abstract Semantic Indexer."""

    INDEX_CLASS: ClassVar[type[AbstractSemanticIndex]]

    docs_dir_path: PathOrStr

    embed_model_class_name: str
    embed_model_name: str
    embed_model_args: Optional[dict[str, Any]] = None

    @abstractmethod
    def persist_index(self, persist_dir_path: PathOrStr, force: bool = False):
        """Persist semantic index of documents."""

@dataclass
class AbstractSemanticIndex(ABC):
    """Abstract Semantic Index."""

    IMPLEMENTATION_NAME: ClassVar[str]

    RETRIEVER_CLASS: ClassVar[type[AbstractSemanticRAG]]

    persist_dir_path: PathOrStr

    @cached_property
    def persist_dir(self) -> Dir:
        """Get the semantic index's persisted directory."""
        return Dir(path=self.persist_dir_path)

    @property
    def exists(self) -> bool:
        """Check if the semantic index exists."""
        return self.persist_dir.exists and (INDEXER_PARAMS_FILE_NAME in self.persist_dir.ls)

    def retriever(self, **kwargs) -> AbstractSemanticRAG:
        """Get semantic retrieval-augmented generator (RAG)."""
        return self.RETRIEVER_CLASS(semantic_index=self, **kwargs)

@dataclass
class AbstractSemanticRAG(ABC):
    """Abstract Semantic Retrieval-Augmented Generator (RAG)."""

    semantic_index: AbstractSemanticIndex

    def __post_init__(self):
        """Post-initialization: load the semantic index's persisted embedding parameters."""
        self.semantic_index_persist_dir: Dir = Dir(path=self.semantic_index.persist_dir_path)

        with self.semantic_index_persist_dir.fs.open(self.semantic_index_persist_dir.sub_path(INDEXER_PARAMS_FILE_NAME),
                                                     mode="rt", encoding="utf-8") as f:
            embed_params: dict[str, Any] = yaml.safe_load(stream=f)

        self.embed_model_class: str = class_from_string(embed_params[EMBED_MODEL_CLASS_KEY])
        self.embed_model_name: str = embed_params[EMBED_MODEL_NAME_KEY]
        self.embed_model_args: dict[str, Any] = embed_params[EMBED_MODEL_ARGS_KEY]

        self.embed_model = self.embed_model_class(model=self.embed_model_name, **self.embed_model_args)

    @abstractmethod
    def retrieve(self, query: str) -> str:
        """Retrieve relevant information from semantic index and synthesize response to query."""
