"""LlamaIndex Vector Store Indexer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from multiprocessing import cpu_count
from typing import Any, ClassVar, Optional

from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.core.readers.file.base import SimpleDirectoryReader
from llama_index.embeddings.openai.base import (
    OpenAIEmbeddingMode,
    OpenAIEmbeddingModelType,
)
import yaml

from dana.contrib.knows.core.fs import Dir, PathOrStr
from dana.contrib.knows.core.knowledge_pack.semantic_index import (
    EMBED_MODEL_ARGS_KEY,
    EMBED_MODEL_CLASS_KEY,
    EMBED_MODEL_NAME_KEY,
    INDEXER_PARAMS_FILE_NAME,
    AbstractSemanticIndex,
    AbstractSemanticIndexer,
)
from dana.contrib.knows.util.misc import class_from_string

from .index import LlamaIndexVectorStore

__all__ = ["LlamaIndexVectorStoreIndexer"]

DEFAULT_LLAMA_INDEX_EMBED_MODEL_CONFIG: dict[str, dict[str, Any]] = {
    "llama_index.embeddings.openai.OpenAIEmbedding": dict(mode=OpenAIEmbeddingMode.SIMILARITY_MODE,
                                                          embed_batch_size=100,
                                                          dimensions=1536,  # 3072,
                                                          additional_kwargs=None,
                                                          api_key=None, api_base=None, api_version=None,
                                                          max_retries=10, timeout=60,
                                                          reuse_client=True,
                                                          callback_manager=None,
                                                          default_headers=None,
                                                          http_client=None, async_http_client=None,
                                                          num_workers=cpu_count())
}

@dataclass
class LlamaIndexVectorStoreIndexer(AbstractSemanticIndexer):
    """LlamaIndex Vector Store Indexer."""

    INDEX_CLASS: ClassVar[type[AbstractSemanticIndex]] = LlamaIndexVectorStore

    embed_model_class_name: str = "llama_index.embeddings.openai.OpenAIEmbedding"
    embed_model_name: str = OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL
    embed_model_args: Optional[dict[str, Any]] = None

    def __post_init__(self):
        """Post-initialization: update embedding model args and create embedding model."""
        assert self.embed_model_class_name in DEFAULT_LLAMA_INDEX_EMBED_MODEL_CONFIG, \
            ValueError(f"Embedding model class {self.embed_model_class_name} not supported")

        default_embed_model_args: dict[str, Any] = DEFAULT_LLAMA_INDEX_EMBED_MODEL_CONFIG[self.embed_model_class_name]

        self.embed_model_args: dict[str, Any] = ({**default_embed_model_args, **self.embed_model_args}
                                                 if self.embed_model_args
                                                 else default_embed_model_args)

        self.embed_model: BaseEmbedding = class_from_string(self.embed_model_class_name)(model=self.embed_model_name,
                                                                                         **self.embed_model_args)

    def persist_index(self, persist_dir_path: PathOrStr, force: bool = False):
        """Create & persist a vector store index from documents if not already persisted.

        Args:
            persist_dir_path: Directory to persist the index
            force: Force the index to be created even if it already exists
        """
        if (not ((index_persist_dir := Dir(path=persist_dir_path)).exists and  # noqa: W504
                 (INDEXER_PARAMS_FILE_NAME in index_persist_dir.ls))) or force:
            docs_dir: Dir = Dir(path=self.docs_dir_path)

            vector_store_index: VectorStoreIndex = VectorStoreIndex.from_documents(
                # BaseIndex.from_documents(...) args:
                # docs.llamaindex.ai/en/stable/api_reference/indices/#llama_index.core.indices.base.BaseIndex.from_documents
                documents=SimpleDirectoryReader(
                    # docs.llamaindex.ai/en/latest/examples/data_connectors/simple_directory_reader.html#full-configuration
                    input_dir=docs_dir.native_str_path,
                    input_files=None,
                    exclude=[
                        ".DS_Store",  # MacOS
                        "*.json",  # JSON files should be indexed differently
                    ],
                    exclude_hidden=False,
                    errors="strict",
                    recursive=True,
                    encoding="utf-8",
                    filename_as_id=False,
                    required_exts=None,
                    file_extractor=None,
                    num_files_limit=None,
                    file_metadata=None,
                    raise_on_error=True,
                    fs=docs_dir.fs).load_data(show_progress=True,
                                              num_workers=1),  # TODO: os.cpu_count()
                storage_context=None,
                show_progress=True,
                callback_manager=None,
                transformations=None,

                # other VectorStoreIndex.__init__(...) args:
                # docs.llamaindex.ai/en/latest/api_reference/indices/vector_store.html#llama_index.core.indices.vector_store.base.VectorStoreIndex
                use_async=False,  # TODO: explore async for optimization
                store_nodes_override=False,
                embed_model=self.embed_model,
                insert_batch_size=2048,
                objects=None,
                index_struct=None)

            vector_store_index.storage_context.persist(persist_dir=persist_dir_path, fs=index_persist_dir.fs)

            with index_persist_dir.fs.open(index_persist_dir.sub_path(INDEXER_PARAMS_FILE_NAME),
                                           mode="wt", encoding="utf-8") as f:
                yaml.dump(data={EMBED_MODEL_CLASS_KEY: self.embed_model_class_name,
                                EMBED_MODEL_NAME_KEY: (self.embed_model_name.value
                                                       if isinstance(self.embed_model_name, Enum)
                                                       else self.embed_model_name),
                                EMBED_MODEL_ARGS_KEY: {k: (v.value if isinstance(v, Enum) else v)
                                                       for k, v in self.embed_model_args.items()},
                                "VECTOR-STORE-PARAMS": {"insert_batch_size": 2048}},
                          stream=f,
                          default_style=None,
                          default_flow_style=False,
                          canonical=False,
                          indent=2,
                          width=80,
                          allow_unicode=True,
                          line_break="\n",
                          encoding="utf-8",
                          explicit_start=None,
                          explicit_end=None,
                          version=None,
                          tags=None,
                          sort_keys=False)
