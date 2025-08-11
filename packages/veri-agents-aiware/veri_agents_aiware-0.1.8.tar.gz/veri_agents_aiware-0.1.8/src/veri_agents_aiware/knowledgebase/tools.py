import logging
import re
from typing import TYPE_CHECKING, Optional, Tuple

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_core.runnables.config import RunnableConfig
from pydantic import BaseModel, Field
from veri_agents_knowledgebase.knowledgebase import KnowledgeFilter
from veri_agents_aiware.knowledgebase.knowledgebase import AiwareKnowledgebase

log = logging.getLogger(__name__)

def _escape_tool_name(name: str) -> str:
    return "".join(re.findall('[a-zA-Z0-9_-]', name.replace("-", "_").replace(" ", "_")))

class AiwareKnowledgebaseQueryInput(BaseModel):
    query: str = Field(
        description="query to search for documents in the knowledgebase."
    )
    documents: Optional[list[str] | str] = Field(
        default=None,
        description="Documents are selected only if they match the document IDs in the list. Useful if you only want to search inside specific documents.",
    )


class AiwareKnowledgebaseQuery(BaseTool):
    """Search for documents in an aiware knowledgebase (that can not be selected by the agent)."""

    name: str = "aiware_kb_retrieve"
    description: str = ""
    args_schema = AiwareKnowledgebaseQueryInput
    response_format: str = "content_and_artifact"  # type: ignore
    handle_tool_errors: bool = True
    num_results: int = 10
    knowledgebase: AiwareKnowledgebase
    """ The knowledgebase to list documents from. This is passed in when the tool is created. """

    name_suffix: str | None = None
    """ You can pass in a suffix to the name of the tool. This is useful if you want to have multiple instances of this tool. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.name_suffix:
            self.name += self.name_suffix

        self.name = _escape_tool_name(self.name)

        self.description = f"Searches for documents in the \"{self.knowledgebase.name}\" knowledgebase."
        if self.knowledgebase.description:
            self.description += f"Use this tool if you're interested in documents about {self.knowledgebase.description}."

    def _create_filter(
        self,
        documents: Optional[list[str] | str] = None,
    ) -> KnowledgeFilter:
        """Create a filter for the knowledgebase from inputs and runnable config

        Args:
            documents: If the document ID is in this list, it will be selected.
        """
        return KnowledgeFilter(
            docs=documents,
        )

    def _run(
        self,
        query: str,
        config: RunnableConfig,
        documents: Optional[list[str] | str] = None,
    ) -> Tuple[list[str], dict]:
        # We tell the LLM if the user has specified any filters
        return_texts = []

        filter = self._create_filter(documents=documents)

        log.info(
            "[AiwareKnowledgebaseQuery] Searching in knowledgebase %s for %s using user filter %s",
            self.knowledgebase.name,
            query,
            filter,
        )
        ret_text, ret_docs = self.knowledgebase.retrieve(
            query, limit=self.num_results, filter=filter
        )
        # log.debug(f"[AiwareKnowledgebaseQuery] Retrieved {len(ret_docs)} documents.")
        if not ret_docs and not ret_text:
            return_texts.append(
                f"No documents found in the knowledgebase for query '{query}'."
            )
        else:
            if ret_text:
                return_texts.append(ret_text)

        return return_texts, {
            "items": ret_docs,
            "type": "document",
            "source": "knowledgebase",
        }

    async def _arun(
        self,
        query: str,
        config: RunnableConfig,
        documents: Optional[list[str] | str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[list[str], dict]:
        # We tell the LLM if the user has specified any filters
        return_texts = []

        filter = self._create_filter(documents=documents)

        log.info(
            f"[AiwareKnowledgebaseQuery] Searching in knowledgebase \"{self.knowledgebase.name}\" for {query} using user filter {filter}"
        )
        try:
            ret_text, ret_docs = await self.knowledgebase.aretrieve(
                query, limit=self.num_results, filter=filter
            )
        except NotImplementedError:
            ret_text, ret_docs = self.knowledgebase.retrieve(
                query, limit=self.num_results, filter=filter
            )
        # log.debug(f"[AiwareKnowledgebaseQuery] Retrieved {len(ret_docs)} documents.")

        if not ret_docs and not ret_text:
            return_texts.append(
                f"No documents found in the knowledgebase for query '{query}'."
            )
        else:
            if ret_text:
                return_texts.append(ret_text)

        return return_texts, {
            "items": ret_docs,
            "type": "document",
            "source": "knowledgebase",
        }

class AiwareKnowledgebaseListDocumentsInput(BaseModel):
    pass

class AiwareKnowledgebaseListDocuments(BaseTool):
    """List documents in an aiware knowledgebase that is not selected by the agent."""

    name: str = "aiware_kb_list_documents"
    description: str = ""
    args_schema = AiwareKnowledgebaseListDocumentsInput
    # response_format: str = "content_and_artifact"  # type: ignore
    handle_tool_errors: bool = True
    knowledgebase: AiwareKnowledgebase
    """ The knowledgebase to list documents from. This is passed in when the tool is created. """

    name_suffix: str | None = None
    """ You can pass in a suffix to the name of the tool. This is useful if you want to have multiple instances of this tool. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.name_suffix:
            self.name += self.name_suffix

        self.name = _escape_tool_name(self.name)

        self.description = (
            f"Lists the documents in the \"{self.knowledgebase.name}\" knowledgebase."
        )
        if self.knowledgebase.description:
            self.description += f"Use this tool if you're interested in documents about {self.knowledgebase.description}."

    def _create_filter(
        self,
    ) -> KnowledgeFilter:
        """Create a filter for the knowledgebase from inputs"""
        return KnowledgeFilter()

    def _run(
        self,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:  # -> Tuple[list[str], dict]:
        log.debug("[AiwareKnowledgebaseListDocuments] Listing documents")

        # filter set by the agent
        filter = self._create_filter()

        docs = self.knowledgebase.get_documents(filter)
        log.debug("[AiwareKnowledgebaseListDocuments] Retrieved documents.")
        return str(
            [
                (
                    d.metadata.get("source"),
                    d.metadata.get("doc_name"),
                    d.metadata.get("last_updated"),
                    d.metadata.get("tags"),
                    d.metadata.get("summary"),
                )
                for d in docs
            ]
        )
