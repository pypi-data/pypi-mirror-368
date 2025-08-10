import logging
from typing import Any, AsyncGenerator, Iterator, Optional, cast
from pydantic import BaseModel
from veri_agents_aiware.aiware_client.client import Aiware
from veri_agents_aiware.aiware_client.graphql.utils import catch_not_found
from veri_agents_aiware.aiware_client.search.models import (
    VectorSearchRequest,
    VectorSearchRequestFilter,
    VectorSearchRequestFilterOperator,
    VectorSearchRequestSemanticSearch,
    VectorSearchRequestSemanticSearchVectorSimilarity,
    VectorSearchResultsResult,
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

log = logging.getLogger(__name__)


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
        name: str = "Aiware",
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
            log.warning("AiwareKnowledgebase.retrieve does not implement filter.pre_tags_any_of parameter")
        if filter.pre_tags_all_of is not None:
            log.warning("AiwareKnowledgebase.retrieve does not implement filter.pre_tags_all_of parameter")
        if filter.tags_any_of is not None:
            log.warning("AiwareKnowledgebase.retrieve does not implement filter.tags_any_of parameter")
        if filter.tags_all_of is not None:
            log.warning("AiwareKnowledgebase.retrieve does not implement filter.tags_all_of parameter")

        return VectorSearchRequestFilter(
            operator=VectorSearchRequestFilterOperator.and_,
            conditions=cast(
                Any,
                and_conditions,
            ),
        )

    def _get_aiware_filter(
        self, filter: KnowledgeFilter | None = None
    ) -> VectorSearchRequestFilter:
        resolved_user_filter = and_filters(self.filter, filter)

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

        if resolved_user_filter is not None:
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

    def retrieve(
        self,
        query: str,
        limit: int,
        filter: KnowledgeFilter | None = None,
        **kwargs,
    ) -> tuple[str | None, list[Document] | None]:
        aiware_filter = self._get_aiware_filter(filter)

        query_embeddings = self.embedding_model.embed_query(query)

        log.warning("AiwareKnowledgebase.retrieve does not implement limit parameter")

        # naive retrieval
        vector_search_res = self.aiware.search.vector_search(
            VectorSearchRequest(
                semanticSearch=VectorSearchRequestSemanticSearch(
                    vectorSimilarity=VectorSearchRequestSemanticSearchVectorSimilarity(
                        rawData=query_embeddings
                    )
                ),
                select=["tags"],
                filters=[aiware_filter],
            )
        )

        results = vector_search_res.results
        if not results:
            return None, None

        # Find all chunks with the same tdo ID and then sort by tdos with most chunks plus score
        ret_prompt = ""
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

        for tdo_id, (tdo_chunks, tdo_score) in chunks_per_tdo.items():
            tdo_res = catch_not_found(
                lambda: self.aiware.graphql.rag_get_tdo_meta(id=tdo_id)
            )

            if tdo_res is None or tdo_res.temporalDataObject is None:
                continue

            tdo = tdo_res.temporalDataObject

            # Sum scores for chunks
            # total_score = sum(chunk_ref.score for chunk_ref in tdo_chunks)

            tdo_meta: dict[str, Any] = {}

            tdo_meta["id"] = tdo.id
            tdo_meta["title"] = tdo.name or "Unknown"
            tdo_meta["relevancy_score"] = f"{tdo_score:.2f}"

            tdo_meta["created_date_time"] = tdo.createdDateTime
            tdo_meta["modified_date_time"] = tdo.modifiedDateTime

            # TODO: attach other aiware info?

            for key, value in tdo_meta.items():
                ret_prompt += f"{key}: {value.__str__()}\n"

            for chunk in tdo_chunks:
                if chunk.model_extra and (tags := chunk.model_extra.get("tags")):
                    chunk_content: str | None = None
                    for tag in cast(list, tags):
                        if tag["key"] == "input":
                            chunk_content = cast(str, tag["value"])
                            break

                    if chunk_content is None:
                        continue

                    aggregate_meta: dict[str, Any] = {}
                    aggregate_meta["doc"] = tdo_meta

                    chunk_meta: dict[str, Any] = {}
                    chunk_meta["relevancy_score"] = chunk.score

                    aggregate_meta["chunk"] = chunk_meta

                    for key, value in chunk_meta.items():
                        ret_prompt += f"{key}: {value.__str__()}\n"

                    ret_prompt += f"{chunk_content}\n\n"
                    ret_docs.append(
                        Document(metadata=aggregate_meta, page_content=chunk_content)
                    )

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
        raise NotImplementedError

    async def aget_documents(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        filter: KnowledgeFilter | None = None,
    ) -> AsyncGenerator[Document, None]:
        """Get all documents from the knowledge base."""
        raise NotImplementedError

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
        raise NotImplementedError
