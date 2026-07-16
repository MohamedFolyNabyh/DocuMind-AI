import logging
from typing import List

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)


class HybridSearchService:

    def __init__(self, vector_service: VectorService):

        self.vector_service = vector_service

        self.indices = {}

        self.reranker = CrossEncoder(
            "BAAI/bge-reranker-base"
        )

        logger.info("Hybrid Search Service Initialized.")

    # --------------------------------------------------------
    # Build BM25 Index
    # --------------------------------------------------------

    def build_bm25(self,source: str,documents: List[Document]):
        logger.info("Building BM25 for %s", source)

        corpus =[doc.page_content.split() for doc in documents]

        bm25 = BM25Okapi(corpus)

        self.indices[source] = {"documents": documents, "bm25": bm25}

        logger.info("BM25 index created for %s.", source)
    # --------------------------------------------------------
    # Dense Search (Qdrant)
    # --------------------------------------------------------

    def dense_search(self,source: str,query: str,k: int = 10):

        logger.info("Running Dense Search...")

        return self.vector_service.similarity_search(source=source,query=query,k=k)

    # --------------------------------------------------------
    # BM25 Search
    # --------------------------------------------------------

    def keyword_search(self,source: str,query: str,k: int = 10):
        logger.info("Running BM25 Search...")

        if source not in self.indices:

            logger.warning("No BM25 index found.")

            return []

        bm25 = self.indices[source]["bm25"]

        documents = self.indices[source]["documents"]

        scores = bm25.get_scores(query.split())

        ranked = sorted(zip(scores, documents),key=lambda x: x[0],reverse=True)

        return [doc for _, doc in ranked[:k]]
    # --------------------------------------------------------
    # Reciprocal Rank Fusion
    # --------------------------------------------------------

    def reciprocal_rank_fusion(
        self,
        dense_docs: List[Document],
        keyword_docs: List[Document],
        k: int = 60
    ) -> List[Document]:

        logger.info("Applying Reciprocal Rank Fusion...")

        scores = {}

        for rank, doc in enumerate(dense_docs):

            key = doc.page_content

            if key not in scores:

                scores[key] = {
                    "document": doc,
                    "score": 0.0
                }

            scores[key]["score"] += 1 / (k + rank + 1)

        for rank, doc in enumerate(keyword_docs):

            key = doc.page_content

            if key not in scores:

                scores[key] = {
                    "document": doc,
                    "score": 0.0
                }

            scores[key]["score"] += 1 / (k + rank + 1)

        ranked = sorted(
            scores.values(),
            key=lambda item: item["score"],
            reverse=True
        )

        logger.info(
            "RRF returned %d merged documents.",
            len(ranked)
        )

        return [
            item["document"]
            for item in ranked
        ]

    # --------------------------------------------------------
    # Cross Encoder Re-ranking
    # --------------------------------------------------------

    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: int = 5
    ) -> List[Document]:

        logger.info("Running CrossEncoder reranking...")

        if not documents:
            return []

        pairs = [
            (query, doc.page_content)
            for doc in documents
        ]

        scores = self.reranker.predict(
            pairs
        )

        ranked = sorted(
            zip(scores, documents),
            key=lambda item: item[0],
            reverse=True
        )

        return [
            doc
            for _, doc in ranked[:top_k]
        ]

    # --------------------------------------------------------
    # Complete Hybrid Search
    # --------------------------------------------------------

    def search(self,query: str,source: str,top_k: int = 5) -> List[Document]:

        logger.info("=" * 60)
        logger.info("Hybrid Search Started")
        logger.info("Query: %s", query)

        dense_results = self.dense_search(query=query,source=source, k=10)

        keyword_results = self.keyword_search(
            query=query,source=source,
            k=10
        )

        merged_results = self.reciprocal_rank_fusion(
            dense_docs=dense_results,
            keyword_docs=keyword_results
        )

        final_results = self.rerank(
            query=query,
            documents=merged_results,
            top_k=top_k
        )

        logger.info(
            "Hybrid Search Finished (%d documents).",
            len(final_results)
        )

        logger.info("=" * 60)

        return final_results