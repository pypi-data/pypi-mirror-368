"""LlamaIndex Vector Store."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from dana.contrib.knows.core.knowledge_pack.semantic_index.abstract import (
    AbstractSemanticIndex,
    AbstractSemanticRAG,
)

from .retriever import LlamaIndexVectorRAG

__all__ = ["LlamaIndexVectorStore"]

@dataclass
class LlamaIndexVectorStore(AbstractSemanticIndex):
    IMPLEMENTATION_NAME: ClassVar[str] = "LLAMA_INDEX_VECTOR_STORE"

    RETRIEVER_CLASS: ClassVar[type[AbstractSemanticRAG]] = LlamaIndexVectorRAG
