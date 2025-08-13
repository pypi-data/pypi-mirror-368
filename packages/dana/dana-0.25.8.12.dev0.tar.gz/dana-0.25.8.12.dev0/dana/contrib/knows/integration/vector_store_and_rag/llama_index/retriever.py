"""LlamaIndex Vector Store RAG."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Optional

from llama_index.core.indices.loading import load_index_from_storage
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.core.llms import LLM
from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers.type import ResponseMode
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.vector_stores.types import VectorStoreQueryMode
from loguru import logger

from dana.contrib.knows.core.knowledge_pack.semantic_index.abstract import (
    AbstractSemanticRAG,
)
from dana.contrib.knows.util.misc import class_from_string

__all__ = ["LlamaIndexVectorRAG"]

DEFAULT_LLAMA_INDEX_RAG_LLM_CONFIG: dict[str, Any] = {
    "llama_index.llms.openai.OpenAI": dict(model="gpt-4o-mini",
                                           temperature=0,
                                           max_tokens=None,
                                           additional_kwargs={"seed": 7 * 17 * 14717},
                                           max_retries=3, timeout=60, reuse_client=True,
                                           api_key=None, api_base=None, api_version=None,
                                           callback_manager=None, default_headers=None,
                                           http_client=None, async_http_client=None,
                                           openai_client=None, async_openai_client=None,
                                           system_prompt=None, messages_to_prompt=None, completion_to_prompt=None,
                                           output_parser=None,
                                           strict=False)
}

DEFAULT_LLAMA_INDEX_RAG_QUERY_ENGINE_CONFIG: dict[str, Any] = dict(
    # other VectorIndexRetriever.__init__(...) args:
    # docs.llamaindex.ai/en/latest/api_reference/query/retrievers/vector_store.html#llama_index.core.indices.vector_store.retrievers.retriever.VectorIndexRetriever
    similarity_top_k=12,
    vector_store_query_mode=VectorStoreQueryMode.MMR,
    filters=None,
    alpha=None,
    doc_ids=None,
    sparse_top_k=None,
    vector_store_kwargs={"mmr_threshold": 0.5},

    verbose=False,

    # other RetrieverQueryEngine.from_args(...) args:
    # docs.llamaindex.ai/en/latest/api_reference/query/query_engines/retriever_query_engine.html#llama_index.core.query_engine.retriever_query_engine.RetrieverQueryEngine.from_args
    response_synthesizer=None,
    node_postprocessors=None,
    response_mode=ResponseMode.COMPACT,
    text_qa_template=None,
    refine_template=None,
    summary_template=None,
    simple_template=None,
    output_cls=None,
    use_async=False,
    streaming=False,
)

@dataclass
class LlamaIndexVectorRAG(AbstractSemanticRAG):
    """LlamaIndex Vector RAG LLM Integration."""

    llm_class_name: str = "llama_index.llms.openai.OpenAI"
    llm_args: Optional[dict[str, Any]] = None

    query_engine_args: Optional[dict[str, Any]] = None

    def __post_init__(self):
        """Post-initialization: update embedding model & LLM args and create those models."""
        super().__post_init__()

        assert self.llm_class_name in DEFAULT_LLAMA_INDEX_RAG_LLM_CONFIG, \
            ValueError(f"LLM class {self.llm_class_name} not supported")

        default_llm_args: dict[str, Any] = DEFAULT_LLAMA_INDEX_RAG_LLM_CONFIG[self.llm_class_name]

        self.llm_args: dict[str, Any] = ({**default_llm_args, **self.llm_args}
                                         if self.llm_args
                                         else default_llm_args)

        self.llm: LLM = class_from_string(self.llm_class_name)(**self.llm_args)

        self.query_engine_args: dict[str, Any] = ({**DEFAULT_LLAMA_INDEX_RAG_QUERY_ENGINE_CONFIG, **self.query_engine_args}  # noqa: E501
                                                  if self.query_engine_args
                                                  else DEFAULT_LLAMA_INDEX_RAG_QUERY_ENGINE_CONFIG)

        self.query_engine: RetrieverQueryEngine = self.index.as_query_engine(embed_model=self.embed_model,
                                                                             llm=self.llm,
                                                                             **self.query_engine_args)

    @cached_property
    def index(self) -> VectorStoreIndex:
        logger.debug(f"Loading index from {self.semantic_index_persist_dir.local.path}...")

        idx = load_index_from_storage(
            storage_context=StorageContext.from_defaults(
                # docs.llamaindex.ai/en/stable/api_reference/storage/storage_context/#llama_index.core.storage.storage_context.StorageContext.from_defaults
                docstore=None,
                index_store=None,
                vector_store=None,
                image_store=None,
                vector_stores=None,
                graph_store=None,
                property_graph_store=None,
                persist_dir=str(self.semantic_index_persist_dir.local.path),
                fs=None),
            index_id=None,

            # other BaseIndex.__init__(...) args:
            # docs.llamaindex.ai/en/stable/api_reference/indices/#llama_index.core.indices.base.BaseIndex
            nodes=None,
            objects=None,
            callback_manager=None,
            transformations=None,
            show_progress=True)

        logger.debug("Index loaded")

        return idx

    def retrieve(self, query: str) -> str:
        """Query the semantic index and synthesize response to query."""
        return self.query_engine.query(query).response
