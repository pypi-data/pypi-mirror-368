"""Vector Store and RAG Integrations."""

from dana.contrib.knows.core.knowledge_pack.semantic_index.abstract import (  # noqa: E501
    AbstractSemanticIndex,
    AbstractSemanticIndexer,
)

from .llama_index import (
    LlamaIndexVectorRAG,
    LlamaIndexVectorStore,
    LlamaIndexVectorStoreIndexer,
)

__all__ = [
    "LlamaIndexVectorStoreIndexer", "LlamaIndexVectorStore", "LlamaIndexVectorRAG",
    "VECTOR_STORE_IMPLEMENTATION_MAP",
]

VECTOR_STORE_IMPLEMENTATION_MAP: dict[str, type[AbstractSemanticIndex]] = {
    LlamaIndexVectorStore.IMPLEMENTATION_NAME: LlamaIndexVectorStore,
}

VECTOR_STORE_INDEXER_FOR_INDEX_CLASS_MAP: dict[type[AbstractSemanticIndex], type[AbstractSemanticIndexer]] = {
    LlamaIndexVectorStore: LlamaIndexVectorStoreIndexer,
}
