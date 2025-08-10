import logging
from typing import Any, AsyncGenerator, Iterator

import cachetools.func
from langchain_core.documents import Document
from langchain_core.tools import BaseTool
from langchain_core.embeddings import Embeddings
from langchain_core.messages.utils import count_tokens_approximately
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.models import Filter
from qdrant_client.models import Distance, VectorParams
from veri_agents_knowledgebase.knowledgebase import (
    Knowledgebase,
    KnowledgeFilter,
    and_filters,
)
from veri_agents_knowledgebase.qdrant.qdrant_doc_store import QdrantDocStore
from veri_agents_knowledgebase.tools.knowledge_retrieval import (
    FixedKnowledgebaseListDocuments,
    FixedKnowledgebaseWithTagsQuery,
)

log = logging.getLogger(__name__)


class QdrantKnowledgebase(Knowledgebase):
    def __init__(
        self,
        vectordb_url: str,
        embedding_model: Embeddings,
        filter: KnowledgeFilter | None = None,
        retrieve_summaries: bool = True,
        retrieve_parents: bool = True,
        retrieve_parents_max_tokens: int = 10000,
        retrieve_parents_num: int = 3,
        retrieve_total_tokens: int = 70000,
        **kwargs,
    ):
        """Initialize the Qdrant knowledge base.
        
        Args:
            vectordb_url (str): The URL of the Qdrant vector database.
            embedding_model (Embeddings): The embedding model to use for vectorization.
            filter (KnowledgeFilter | None): Optional filter to apply to the knowledge base.
            retrieve_summaries (bool): Whether to retrieve summaries of documents and add them to the context.
            retrieve_parents (bool): Whether to retrieve parent documents of retrieved chunks.
            retrieve_parents_max_tokens (int): Maximum tokens for retrieving parent documents, otherwise chunks are used.
            retrieve_parents_num (int): Number of parent documents to retrieve, the ones with top relevancy scores will be selected.
            retrieve_total_tokens (int): Total tokens limit for retrieval.
        """
        super().__init__(**kwargs)
        self.chunks_collection_name = f"chunks_{self.metadata.collection}"
        self.docs_collection_name = f"docs_{self.metadata.collection}"
        self.filter = filter
        self.retrieve_summaries = retrieve_summaries
        self.retrieve_parents = retrieve_parents
        self.retrieve_parents_max_tokens = retrieve_parents_max_tokens
        self.retrieve_parents_num = retrieve_parents_num
        self.retrieve_total_tokens = retrieve_total_tokens

        self.embedding_model = embedding_model

        log.info(f"Connecting to Qdrant at {vectordb_url}")
        self.qdrant = QdrantClient(vectordb_url)
        self._init_collection()
        sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        self.vector_store = QdrantVectorStore(
            client=self.qdrant,
            collection_name=self.chunks_collection_name,
            # FIXME
            embedding=self.embedding_model,  # pyright: ignore[reportArgumentType]
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_embedding=sparse_embeddings,
            sparse_vector_name="sparse",
        )
        self.doc_store = QdrantDocStore(
            client=self.qdrant, collection_name=self.docs_collection_name
        )
        self.doc_store.create_schema()

    def _init_collection(self):
        if not self.qdrant.collection_exists(self.chunks_collection_name):
            self.qdrant.create_collection(
                self.chunks_collection_name,
                vectors_config={
                    "dense": VectorParams(
                        size=1024, distance=Distance.COSINE
                    )  # TODO get size from somewhere
                },
                sparse_vectors_config={
                    "sparse": models.SparseVectorParams(),
                },
            )

    @cachetools.func.ttl_cache(maxsize=1, ttl=360)
    def _load_tags(self):
        """Load tags from the documents in the knowledge base."""
        tags = self.metadata.tags
        for doc in self.doc_store.yield_documents():
            if doc.metadata and "tags" in doc.metadata:
                doc_tags = doc.metadata["tags"]
                if isinstance(doc_tags, str):
                    doc_tags = [doc_tags]
                for doc_tag in doc_tags:
                    if doc_tag not in tags:
                        tags[doc_tag] = ""
        return tags

    @property
    def tags(self):
        """Get the tags for the workflow."""
        return self._load_tags()

    def retrieve(
        self,
        query: str,
        limit: int,
        filter: KnowledgeFilter | None = None,
        **kwargs,
    ) -> tuple[str | None, list[Document] | None]:
        # for now let's do naive retrieval
        qdrant_filter = self._create_qdrant_filter(and_filters(filter, self.filter))
        log.debug("Qdrant Filter: %s", qdrant_filter)
        sub_docs = self.vector_store.similarity_search_with_score(
            query, k=limit, filter=qdrant_filter
        )
        if not sub_docs:
            return None, None
        
        # Find all documents with the same parent ID and then sort by documents with most chunks plus score
        ret_prompt = ""
        ret_docs = []
        subdocs_per_doc: dict[str, list[tuple[Document, float]]] = {}
        for d, score in sub_docs:
            if "source" in d.metadata and d.metadata["source"] not in subdocs_per_doc:
                subdocs_per_doc.setdefault(d.metadata["source"], []).append((d, score))

        # Get all scores and select the top n parent documents
        top_parent_docs = sorted(
            subdocs_per_doc.items(),
            key=lambda item: sum(score for _, score in item[1]),
            reverse=True,
        )[: self.retrieve_parents_num]
        top_parent_doc_ids = [doc_id for doc_id, _ in top_parent_docs]

        # Now for each parent document, retrieve the full document
        for parent_id, sub_docs in subdocs_per_doc.items():
            parent_docs = self.doc_store.mget([parent_id])
            if parent_docs and parent_docs[0]:
                parent_doc = parent_docs[0]

                # Sum scores for sub docs
                total_score = sum(score for _, score in sub_docs)

                # Add metdata to the prompt, including title
                ret_prompt += f"Title: {parent_doc.metadata.get('title', 'Unknown')}\n"
                if tags := parent_doc.metadata.get("tags"):
                    ret_prompt += f"Tags: {', '.join(tags)}\n"
                ret_prompt += f"Source: {parent_doc.metadata.get('source', 'Unknown')}\n"
                ret_prompt += f"Relevancy score: {total_score:.2f}\n"
                ret_prompt += f"Last Updated: {parent_doc.metadata.get('last_updated', 'Unknown')}\n\n"

                # Attach summary
                if self.retrieve_summaries and "summary" in parent_doc.metadata:
                    ret_prompt += f"{parent_doc.metadata['summary']}\n"

                # Check if document is too long, then either attach the full document or just the chunks
                if (self.retrieve_parents and
                      (count_tokens_approximately([parent_doc.page_content]) < self.retrieve_parents_max_tokens) and
                      parent_id in top_parent_doc_ids):
                    ret_prompt += f"Full Document:\n{parent_doc.page_content}\n\n"
                    ret_docs.append(parent_doc)
                else:
                    ret_prompt += "Relevant chunks:\n"
                    for sub_doc, score in sub_docs:
                        # Don't attach summaries to the prompt but return for the source list
                        ret_docs.append(sub_doc)
                        if sub_doc.metadata.get("summary"):
                            continue
                        # Attach headings if available
                        if "headings" in sub_doc.metadata and sub_doc.metadata["headings"]:
                            ret_prompt += f"Heading: {sub_doc.metadata['headings'][0]}\n"
                        ret_prompt += f"{sub_doc.page_content}\n\n"
                ret_prompt += "---- End of document" + "\n\n"
        
        # truncate return prompt and documents if they exceed the total token limit
        if ret_prompt and count_tokens_approximately([ret_prompt]) > self.retrieve_total_tokens:
            ret_prompt = ret_prompt[:self.retrieve_total_tokens]

        log.debug("Retrieve prompt: %s", ret_prompt.strip())

        return ret_prompt.strip(), ret_docs
        

    def get_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> Iterator[Document]:
        qdrant_filter = self._create_qdrant_filter(and_filters(filter, self.filter))
        return self.doc_store.yield_documents(filter=qdrant_filter)

    async def aget_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> AsyncGenerator[Document, None]:
        """Get all documents from the knowledge base."""
        qdrant_filter = self._create_qdrant_filter(filter)
        for doc in self.doc_store.yield_documents(filter=qdrant_filter):
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
        tools = []
        if retrieve_tools:
            tools.append(
                FixedKnowledgebaseWithTagsQuery(
                    knowledgebase=self,
                    num_results=kwargs.get("num_results", 10),
                    name_suffix=f"_{self.metadata.collection if name_suffix is None else name_suffix}",
                    runnable_config_filter_prefix=runnable_config_filter_prefix or "filter_",
                )
            )
        if list_tools:
            tools.append(
                FixedKnowledgebaseListDocuments(
                    knowledgebase=self,
                    name_suffix=f"_{self.metadata.collection if name_suffix is None else name_suffix}",
                    runnable_config_filter_prefix=runnable_config_filter_prefix or "filter_",
                )
            )
        return tools

    def _create_qdrant_filter(
        self,
        filter: KnowledgeFilter | None = None,
    ):
        """Create a Qdrant filter from the knowledgebase filter.
        Args:
            filter (KnowledgeFilter): The knowledge filter to convert.
        Returns:
            Filter: The Qdrant filter.
        """
        if not filter:
            return None

        must = []
        # doc filter means all the documents in the list (so a should clause)
        if filter.docs:
            doc_filter = filter.docs
            if isinstance(filter.docs, str):
                doc_filter = [filter.docs]
            should = []
            for doc_id in doc_filter:
                should.append(
                    models.FieldCondition(
                        key="metadata.source", match=models.MatchValue(value=doc_id)
                    )
                )
            must.append(Filter(should=should))
        if filter.tags_any_of:
            tag_any_filter = filter.tags_any_of
            if isinstance(filter.tags_any_of, str):
                tag_any_filter = [filter.tags_any_of]
            should = []
            for tag in tag_any_filter:
                should.append(
                    models.FieldCondition(
                        key="metadata.tags",
                        match=models.MatchValue(value=tag),
                    )
                )
            must.append(Filter(should=should))
        if filter.tags_all_of:
            tag_all_filter = filter.tags_all_of
            if isinstance(filter.tags_all_of, str):
                tag_all_filter = [filter.tags_all_of]
            for tag in tag_all_filter:
                must.append(
                    models.FieldCondition(
                        key="metadata.tags",
                        match=models.MatchValue(value=tag),
                    )
                )
        if filter.pre_tags_any_of:
            pre_tag_any_filter = filter.pre_tags_any_of
            if isinstance(filter.pre_tags_any_of, str):
                pre_tag_any_filter = [filter.pre_tags_any_of]
            should = []
            for tag in pre_tag_any_filter:
                should.append(
                    models.FieldCondition(
                        key="metadata.tags",
                        match=models.MatchValue(value=tag),
                    )
                )
            must.append(Filter(should=should))
        if filter.pre_tags_all_of:
            pre_tag_all_filter = filter.pre_tags_all_of
            if isinstance(filter.pre_tags_all_of, str):
                pre_tag_all_filter = [filter.pre_tags_all_of]
            for tag in pre_tag_all_filter:
                must.append(
                    models.FieldCondition(
                        key="metadata.tags",
                        match=models.MatchValue(value=tag),
                    )
                )
        return Filter(must=must) if must else None
