import logging
from typing import Any, AsyncGenerator, Iterator, TypedDict, cast
from pydantic import Field
from veri_agents_aiware.aiware_client.client import Aiware
from veri_agents_aiware.aiware_client.graphql.client.fragments import TDOMeta
from veri_agents_aiware.aiware_client.search.models import (
    VectorSearchRequest,
    VectorSearchRequestFilter,
    VectorSearchRequestFilterOperator,
    VectorSearchRequestSemanticSearch,
    VectorSearchRequestSemanticSearchVectorSimilarity,
    VectorSearchResultsResultVector,
)
from veri_agents_aiware.utils import not_none
from veri_agents_knowledgebase import Knowledgebase, KnowledgeFilter
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.tools import BaseTool
from langchain_core.messages.utils import count_tokens_approximately
import cachetools.func
from veri_agents_knowledgebase.knowledgebase import and_filters
import yaml

log = logging.getLogger(__name__)


class TDODocumentMetadata(TypedDict):
    id: str
    name: str
    created_date_time: str | None
    modified_date_time: str | None


class TDODocument(Document):
    metadata: TDODocumentMetadata  # pyright: ignore[reportGeneralTypeIssues, reportIncompatibleVariableOverride]


class ChunkDocumentMetadataChunk(TypedDict):
    relevancy_score: float


class ChunkDocumentMetadata(TypedDict):
    parent_doc: TDODocumentMetadata
    chunk: ChunkDocumentMetadataChunk


class ChunkDocument(Document):
    metadata: ChunkDocumentMetadata  # pyright: ignore[reportGeneralTypeIssues, reportIncompatibleVariableOverride]


class StructuredChunkRes(ChunkDocumentMetadataChunk):
    content: str


class StructuredTDORes(TypedDict):
    parent_doc: TDODocumentMetadata
    chunks: list[StructuredChunkRes]


Default_AiwareKnowledgebase_Name = "Aiware"


class AiwareKnowledgebase(Knowledgebase):
    def __init__(
        self,
        aiware: Aiware,
        embedding_model_name: str,
        embedding_model: Embeddings,
        filter: KnowledgeFilter | None = None,
        # retrieve_summaries: bool = True,
        # retrieve_parents: bool = True,
        # retrieve_parents_max_tokens: int = 10000,
        # retrieve_parents_num: int = 3,
        retrieve_total_tokens: int = 70000,
        name: str = Default_AiwareKnowledgebase_Name,
        **kwargs,
    ):
        """Initialize the Aiware knowledge base.

        Args:
            aiware (Aiware): The Aiware client (with auth)
            embedding_model_name (str): The name of the embedding model - used for DB slicing.
            embedding_model (Embeddings): The embedding model to use for vectorization.
            filter (KnowledgeFilter | None): Optional filter to apply to the knowledge base.
        """
        super().__init__(name=name, **kwargs)

        self.aiware = aiware

        self.filter = filter
        # self.retrieve_summaries = retrieve_summaries
        # self.retrieve_parents = retrieve_parents
        # self.retrieve_parents_max_tokens = retrieve_parents_max_tokens
        # self.retrieve_parents_num = retrieve_parents_num
        self.retrieve_total_tokens = retrieve_total_tokens

        self.embedding_model_name = embedding_model_name
        self.embedding_model = embedding_model

    @cachetools.func.ttl_cache(maxsize=1, ttl=360)
    def _load_tags(self) -> dict[str, str]:
        """Load tags from the documents in the knowledge base."""
        tags = self.metadata.tags
        # TODO
        return tags

    @property
    def tags(self):
        """Get the tags for the workflow."""
        return self._load_tags()

    @staticmethod
    def _to_aiware_filter(filter: KnowledgeFilter) -> VectorSearchRequestFilter:
        and_conditions: list[VectorSearchRequestFilter] = []

        if filter.docs is not None:
            docs = filter.docs if isinstance(filter.docs, list) else [filter.docs]
            docs_conditions: list[VectorSearchRequestFilter] = []
            for doc in docs:
                docs_conditions.append(
                    VectorSearchRequestFilter(
                        operator=VectorSearchRequestFilterOperator.term,
                        field="recordingId",
                        value=doc,
                    )
                )
            and_conditions.append(
                VectorSearchRequestFilter(
                    operator=VectorSearchRequestFilterOperator.or_,
                    conditions=cast(
                        Any,
                        docs_conditions,
                    ),
                )
            )

        if filter.pre_tags_any_of is not None:
            log.warning(
                "AiwareKnowledgebase.retrieve does not support filter.pre_tags_any_of parameter"
            )
        if filter.pre_tags_all_of is not None:
            log.warning(
                "AiwareKnowledgebase.retrieve does not support filter.pre_tags_all_of parameter"
            )
        if filter.tags_any_of is not None:
            log.warning(
                "AiwareKnowledgebase.retrieve does not support filter.tags_any_of parameter"
            )
        if filter.tags_all_of is not None:
            log.warning(
                "AiwareKnowledgebase.retrieve does not support filter.tags_all_of parameter"
            )

        return VectorSearchRequestFilter(
            operator=VectorSearchRequestFilterOperator.and_,
            conditions=cast(
                Any,
                and_conditions,
            ),
        )

    def _resolve_filter(self, filter: KnowledgeFilter | None = None) -> KnowledgeFilter:
        resolved_filter = and_filters(self.filter, filter)

        if resolved_filter is None or not resolved_filter.docs:
            raise RuntimeError("filter.docs is required")

        return resolved_filter

    def _get_aiware_filter(
        self, filter: KnowledgeFilter | None = None
    ) -> VectorSearchRequestFilter:
        aiware_filters: list[VectorSearchRequestFilter] = [
            VectorSearchRequestFilter(
                operator=VectorSearchRequestFilterOperator.term,
                field="tags.key",
                value="embedding-model",
            ),
            VectorSearchRequestFilter(
                operator=VectorSearchRequestFilterOperator.term,
                field="tags.value",
                value=self.embedding_model_name,
            ),
        ]

        resolved_user_filter = self._resolve_filter(filter=filter)

        aiware_filters.append(
            AiwareKnowledgebase._to_aiware_filter(resolved_user_filter)
        )

        return VectorSearchRequestFilter(
            operator=VectorSearchRequestFilterOperator.and_,
            conditions=cast(
                Any,
                aiware_filters,
            ),
        )

    def _doc_from_tdo(self, tdo: TDOMeta) -> TDODocument:
        tdo_meta: TDODocumentMetadata = {
            "id": tdo.id,
            "name": tdo.name or "Unknown",
            "created_date_time": tdo.createdDateTime.__str__(),
            "modified_date_time": tdo.modifiedDateTime.__str__(),
        }

        return TDODocument(metadata=tdo_meta, page_content="")

    def _doc_from_chunk(
        self, tdo_doc: TDODocument, chunk: VectorSearchResultsResultVector
    ) -> ChunkDocument:
        chunk_content: str = ""
        chunk_meta: ChunkDocumentMetadata = {
            "parent_doc": tdo_doc.metadata,
            "chunk": {"relevancy_score": chunk.score},
        }

        if chunk.model_extra and (tags := chunk.model_extra.get("tags")):
            for tag in cast(list, tags):
                if tag["key"] == "input":
                    chunk_content = cast(str, tag["value"])
                    break

        return ChunkDocument(metadata=chunk_meta, page_content=chunk_content)

    def retrieve(
        self,
        query: str,
        limit: int,
        filter: KnowledgeFilter | None = None,
        **kwargs,
    ) -> tuple[str | None, list[Document] | None]:
        aiware_filter = self._get_aiware_filter(filter)

        query_embeddings = self.embedding_model.embed_query(query)

        vector_search_res = self.aiware.search.vector_search(
            VectorSearchRequest(
                limit=limit,
                semanticSearch=VectorSearchRequestSemanticSearch(
                    vectorSimilarity=VectorSearchRequestSemanticSearchVectorSimilarity(
                        rawData=query_embeddings
                    ),
                ),
                select=["tags"],
                filters=[aiware_filter],
            )
        )

        results = vector_search_res.results
        if not results:
            return None, None

        # Find all chunks with the same tdo ID and then sort by tdos with most chunks plus score
        ret_structured: list[StructuredTDORes] = []
        ret_docs: list[Document] = []

        chunks_per_tdo: dict[
            str, tuple[list[VectorSearchResultsResultVector], float]
        ] = {
            not_none(result.recordingId): (result.vectors, result.score)
            for result in results
        }

        # # Get all scores and select the top n tdos
        # top_tdos = sorted(
        #     chunks_per_tdo.items(),
        #     key=lambda item: sum(chunk_ref.score for chunk_ref in item[1]),
        #     reverse=True,
        # )[: self.retrieve_parents_num]
        # top_tdo_ids = [tdo_id for tdo_id, _ in top_tdos]

        tdo_ids = [tdo_id for tdo_id in chunks_per_tdo.keys()]
        tdos_res = self.aiware.graphql.rag_get_td_os_meta(
            ids=tdo_ids, idsCount=len(tdo_ids)
        )

        if (
            tdos_res.temporalDataObjects is None
            or tdos_res.temporalDataObjects.records is None
        ):
            return None, None

        tdos: dict[str, TDOMeta] = {}
        for tdo_res in tdos_res.temporalDataObjects.records:
            if tdo_res is None:
                continue
            tdos[tdo_res.id] = tdo_res

        for tdo_id, (tdo_chunks, _) in chunks_per_tdo.items():
            tdo = tdos.get(tdo_id, None)
            if tdo is None:
                continue

            tdo_doc = self._doc_from_tdo(tdo)

            tdo_ret_chunks: list[StructuredChunkRes] = []
            tdo_ret: StructuredTDORes = {"parent_doc": tdo_doc.metadata, "chunks": []}

            for chunk in tdo_chunks:
                chunk_doc = self._doc_from_chunk(tdo_doc, chunk)

                chunk_ret: StructuredChunkRes = {
                    **chunk_doc.metadata["chunk"],
                    "content": chunk_doc.page_content,
                }

                tdo_ret_chunks.append(chunk_ret)

                ret_docs.append(chunk_doc)

            tdo_ret["chunks"] = tdo_ret_chunks
            ret_structured.append(tdo_ret)

        ret_prompt = yaml.dump(ret_structured, sort_keys=False)

        # truncate return prompt and documents if they exceed the total token limit
        if (
            ret_prompt
            and count_tokens_approximately(ret_prompt) > self.retrieve_total_tokens
        ):
            ret_prompt = ret_prompt[: self.retrieve_total_tokens]

        log.debug("Retrieve prompt: %s", ret_prompt.strip())

        return ret_prompt.strip(), ret_docs

    def get_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> Iterator[Document]:
        """Get all documents from the knowledge base."""
        resolved_user_filter = self._resolve_filter(filter=filter)

        if not resolved_user_filter.docs_list:
            raise RuntimeError(
                "filter (in constructor or as arg) is required for get_documents"
            )

        tdo_ids = resolved_user_filter.docs_list
        tdos_res = self.aiware.graphql.rag_get_td_os_meta(
            ids=tdo_ids, idsCount=len(tdo_ids)
        )

        if (
            tdos_res.temporalDataObjects is None
            or tdos_res.temporalDataObjects.records is None
        ):
            return iter([])

        docs: list[Document] = []

        for tdo_res in tdos_res.temporalDataObjects.records:
            if tdo_res is None:
                continue

            tdo = tdo_res

            tdo_doc = self._doc_from_tdo(tdo)
            docs.append(tdo_doc)

        return iter(docs)

    async def aget_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> AsyncGenerator[Document, None]:
        """Get all documents from the knowledge base."""
        for doc in self.get_documents(filter=filter):
            yield doc

    def get_tools(
        self,
        retrieve_tools: bool = True,
        list_tools: bool = True,
        write_tools: bool = False,
        name_suffix: str | None = None,
        runnable_config_filter_prefix: str | None = None,
        **kwargs: Any,
    ) -> list[BaseTool]:
        """Get agent tools to access this knowledgebase.

        Args:
            retrieve_tools (bool): Whether to include tools for retrieving documents.
            list_tools (bool): Whether to include tools for listing documents.
            write_tools (bool): Whether to include tools for writing documents.
        Returns:
            list[BaseTool]: List of tools for the knowledge base.
        """
        from veri_agents_aiware.knowledgebase.tools import (
            AiwareKnowledgebaseListDocuments,
            AiwareKnowledgebaseQuery,
        )

        tools = []

        resolved_name_suffix = (
            self.metadata.collection
            or (
                self.metadata.name
                if self.metadata.name != Default_AiwareKnowledgebase_Name
                else None
            )
            if name_suffix is None
            else name_suffix
        )

        if retrieve_tools:
            tools.append(
                AiwareKnowledgebaseQuery(
                    knowledgebase=self,
                    num_results=kwargs.get("num_results", 10),
                    name_suffix=f"_{resolved_name_suffix}" if resolved_name_suffix else None,
                )
            )
        if list_tools:
            tools.append(
                AiwareKnowledgebaseListDocuments(
                    knowledgebase=self,
                    name_suffix=f"_{resolved_name_suffix}" if resolved_name_suffix else None,
                )
            )
        return tools
