"""Knowledge Pack."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from functools import cache, cached_property
from typing import Any, ClassVar, Optional

from llama_index.embeddings.openai.base import OpenAIEmbeddingModelType

from dana.contrib.knows.core.fs import Dir
from dana.contrib.knows.core.knowledge_form import TaskPlan, TextNote
from dana.contrib.knows.integration.vector_store_and_rag import (
    VECTOR_STORE_IMPLEMENTATION_MAP,
    VECTOR_STORE_INDEXER_FOR_INDEX_CLASS_MAP,
    LlamaIndexVectorStore,
    LlamaIndexVectorStoreIndexer,
)

from .semantic_index import (
    INDEXER_PARAMS_FILE_NAME,
    AbstractSemanticIndex,
    AbstractSemanticIndexer,
    AbstractSemanticRAG,
)

__all__ = ["Kpk"]

@dataclass(init=True,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False,
           match_args=True,
           kw_only=False,
           slots=False,
           weakref_slot=False)
class Kpk(Dir):
    """Knowledge Pack."""

    CONTENT_KEY: ClassVar[str] = "CONTENT"
    DOCUMENTS_CONTENT_KEY: ClassVar[str] = "DOCUMENTS"
    EXPERT_TEXT_NOTES_CONTENT_KEY: ClassVar[str] = "EXPERT_TEXT_NOTES"
    EXPERT_TASK_PLANS_CONTENT_KEY: ClassVar[str] = "EXPERT_TASK_PLANS"

    INDEXES_KEY: ClassVar[str] = "INDEXES"
    SEMANTIC_INDEXES_KEY: ClassVar[str] = "SEMANTIC"
    SYMBOLIC_INDEXES_KEY: ClassVar[str] = "SYMBOLIC"

    expert_text_notes: list[TextNote] = field(default_factory=list, repr=False)
    expert_task_plans: dict[str, TaskPlan] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        """Load light-weight knowledge content such as Expert Text Notes & Task Plans."""
        super().__post_init__()

        self.load_expert_text_notes()
        self.load_expert_task_plans()

    def __hash__(self) -> int:
        return hash(self.path)

    def load_expert_text_notes(self):
        """Load Expert Text Notes from Knowledge Pack."""
        for text_file_path in self.sub_dir(self.CONTENT_KEY, self.EXPERT_TEXT_NOTES_CONTENT_KEY).glob("*.txt"):
            with self.fs.open(path=text_file_path,
                              mode="rt",
                              block_size=None,
                              cache_options=None,
                              compression=None,
                              encoding="utf-8") as f:
                self.expert_text_notes.append(TextNote(content=f.read()))

    def load_expert_task_plans(self):
        """Load Expert Task Plans from Knowledge Pack."""
        for yaml_file_path in self.sub_dir(self.CONTENT_KEY, self.EXPERT_TASK_PLANS_CONTENT_KEY).glob("*.yml"):
            with self.fs.open(path=yaml_file_path,
                              mode="rt",
                              block_size=None,
                              cache_options=None,
                              compression=None,
                              encoding="utf-8") as f:
                self.expert_task_plans.update(TaskPlan.from_yaml(f))

    def capture(self, new_knowledge):
        """TODO: Capture new knowledge into Knowledge Pack."""

    def organize(
            self,
            semantic_indexer_class: type[AbstractSemanticIndexer] = LlamaIndexVectorStoreIndexer,
            semantic_indexer_embed_model_class_name: Optional[str] = "llama_index.embeddings.openai.OpenAIEmbedding",
            semantic_indexer_embed_model_name: Optional[str] = OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL,
            semantic_indexer_embed_model_args: Optional[dict[str, Any]] = None,
            force: bool = False):
        """Organize Knowledge Pack."""
        self._persist_semantic_index(semantic_indexer_class=semantic_indexer_class,
                                     embed_model_class_name=semantic_indexer_embed_model_class_name,
                                     embed_model_name=semantic_indexer_embed_model_name,
                                     embed_model_args=semantic_indexer_embed_model_args,
                                     force=force)

        # TODO: organize and persist symbolic index as well

    @cached_property
    def _docs_content_dir(self) -> Dir:
        """Get documents content directory."""
        return self.sub_dir(self.CONTENT_KEY, self.DOCUMENTS_CONTENT_KEY)

    @cached_property
    def _semantic_indexes_dir(self) -> Dir:
        """Get semantic indexes directory."""
        return self.sub_dir(self.INDEXES_KEY, self.SEMANTIC_INDEXES_KEY)

    def _semantic_indexer(
            self,
            semantic_indexer_class: type[AbstractSemanticIndexer] = LlamaIndexVectorStoreIndexer,
            embed_model_class_name: Optional[str] = "llama_index.embeddings.openai.OpenAIEmbedding",
            embed_model_name: Optional[str] = OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL,
            embed_model_args: Optional[dict[str, Any]] = None) -> AbstractSemanticIndexer:
        return semantic_indexer_class(docs_dir_path=self._docs_content_dir.path,
                                      embed_model_class_name=embed_model_class_name,
                                      embed_model_name=embed_model_name,
                                      embed_model_args=embed_model_args)

    def _semantic_index_persist_dir_struct(self, semantic_indexer: AbstractSemanticIndexer) -> tuple[str, str, str]:
        """Get semantic index persist 3-level directory structure."""
        return (semantic_indexer.INDEX_CLASS.IMPLEMENTATION_NAME,
                semantic_indexer.embed_model_class_name,
                (embed_model_name.value
                 if isinstance(embed_model_name := semantic_indexer.embed_model_name, Enum)
                 else embed_model_name))

    def _persist_semantic_index(
            self,
            semantic_indexer_class: type[AbstractSemanticIndexer] = LlamaIndexVectorStoreIndexer,
            embed_model_class_name: Optional[str] = "llama_index.embeddings.openai.OpenAIEmbedding",
            embed_model_name: Optional[str] = OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL,
            embed_model_args: Optional[dict[str, Any]] = None,
            force: bool = False):
        """Persist semantic index."""
        semantic_indexer: AbstractSemanticIndexer = self._semantic_indexer(
            semantic_indexer_class=semantic_indexer_class,
            embed_model_class_name=embed_model_class_name,
            embed_model_name=embed_model_name,
            embed_model_args=embed_model_args)

        semantic_indexer.persist_index(
            persist_dir_path=self._semantic_indexes_dir.sub_path(
                *self._semantic_index_persist_dir_struct(semantic_indexer=semantic_indexer)),
            force=force)

    def retrieve(self, query: str) -> str:
        """Retrieve relevant knowledge from Knowledge Pack."""
        semantic_rag_answer: str = self._get_semantic_rag().retrieve(query=query)

        # TODO: retrieve and combine relevant knowledge from symbolic index and expert text notes

        return semantic_rag_answer

    def _get_or_create_semantic_index(
            self,
            semantic_index_impl_name: Optional[str] = None,
            semantic_indexer_embed_model_class_name: Optional[str] = None,
            semantic_indexer_embed_model_name: Optional[str] = None) -> AbstractSemanticIndex:
        """Get or create semantic index."""
        to_create: bool = False

        if (persisted_semantic_index_impl_names := self._semantic_indexes_dir.direct_sub_dir_names):
            if semantic_index_impl_name is None:
                semantic_index_impl_name: str = persisted_semantic_index_impl_names[0]

            else:
                assert semantic_index_impl_name in VECTOR_STORE_IMPLEMENTATION_MAP
                to_create: bool = semantic_index_impl_name not in persisted_semantic_index_impl_names

            if not to_create:
                semantic_index_impl_sub_dir: Dir = self._semantic_indexes_dir.sub_dir(semantic_index_impl_name)

                if (persisted_embed_model_class_names := semantic_index_impl_sub_dir.direct_sub_dir_names):
                    if semantic_indexer_embed_model_class_name is None:
                        semantic_indexer_embed_model_class_name: str = persisted_embed_model_class_names[0]

                    else:
                        to_create: bool = semantic_indexer_embed_model_class_name not in persisted_embed_model_class_names  # noqa: E501

                    if not to_create:
                        embed_model_class_sub_dir: Dir = \
                            semantic_index_impl_sub_dir.sub_dir(semantic_indexer_embed_model_class_name)

                        if (persisted_embed_model_names := embed_model_class_sub_dir.direct_sub_dir_names):
                            if semantic_indexer_embed_model_name is None:
                                semantic_indexer_embed_model_name: str = persisted_embed_model_names[0]

                            else:
                                to_create: bool = semantic_indexer_embed_model_name not in persisted_embed_model_names

                            if not to_create:
                                index_persist_dir: Dir = \
                                    embed_model_class_sub_dir.sub_dir(semantic_indexer_embed_model_name)

                                to_create: bool = INDEXER_PARAMS_FILE_NAME not in index_persist_dir.ls

        else:
            to_create: bool = True

        if semantic_index_impl_name is None:
            semantic_index_impl_name: str = LlamaIndexVectorStore.IMPLEMENTATION_NAME

        semantic_index_class: type[AbstractSemanticIndex] = VECTOR_STORE_IMPLEMENTATION_MAP[semantic_index_impl_name]

        if to_create:
            self._persist_semantic_index(
                semantic_indexer_class=VECTOR_STORE_INDEXER_FOR_INDEX_CLASS_MAP[semantic_index_class],
                embed_model_class_name=semantic_indexer_embed_model_class_name,
                embed_model_name=semantic_indexer_embed_model_name,
                force=True)

        return semantic_index_class(
            persist_dir_path=self._semantic_indexes_dir.sub_path(semantic_index_impl_name,
                                                                 semantic_indexer_embed_model_class_name,
                                                                 semantic_indexer_embed_model_name))

    @cache
    def _get_semantic_rag(self,
                          semantic_index_impl_name: Optional[str] = None,
                          semantic_indexer_embed_model_class_name: Optional[str] = None,
                          semantic_indexer_embed_model_name: Optional[str] = None,
                          **semantic_rag_kwargs) -> AbstractSemanticRAG:
        """Get query engine based on semantic document index."""
        semantic_index: AbstractSemanticIndex = self._get_or_create_semantic_index(
            semantic_index_impl_name=semantic_index_impl_name,
            semantic_indexer_embed_model_class_name=semantic_indexer_embed_model_class_name,
            semantic_indexer_embed_model_name=semantic_indexer_embed_model_name)

        return semantic_index.retriever(**semantic_rag_kwargs)

    def apply(self, target: str, **kwargs):
        """TODO: Apply Knowledge Pack to specified target consumer agentic-AI tool."""

    def learn(self, **kwargs):
        """TODO: Learn from feedback and update Knowledge Pack."""
