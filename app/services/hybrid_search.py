import logging
from typing import List
from langchain_core.documents import Document
from rank_bm25 import BM25OKapi
from sentence_transformers import CrossEncoder
from app.services.vector_service import VectorService

logger=logging.getLogger(__name__)




class HybridSearchService:

    def __init__(self, vector_service: VectorService):

        self.vector_service = vector_service

        # سيتم بناؤه بعد رفع الـ PDFs
        self.bm25 = None

        self.documents: List[Document] = []

        # Cross Encoder لإعادة ترتيب النتائج
        self.reranker = CrossEncoder(
            "BAAI/bge-reranker-base"
        )

        logger.info(
            "Hybrid Search Service Initialized."
        )
    def build_bm25(self,documents: List[Document]) -> None:
        logger.info("Building BM25 Index..." )

        self.documents = documents

        corpus = [
        doc.page_content.split()
        for doc in documents
        ]

        self.bm25 = BM25Okapi(corpus)

        logger.info("BM25 Ready.")
    def dense_search(self,query: str,k: int = 10) -> List[Document]:
    """
    Dense Search using Qdrant.
    """

         logger.info(
        "Dense Search..."
         )

        return self.vector_service.similarity_search(query=query,k=k)
    def keyword_search( self,query: str,k: int = 10) -> List[Document]:
    """
    BM25 Search
    """

        if self.bm25 is None:

        logger.warning(
            "BM25 not initialized."
        )

        return []

        scores = self.bm25.get_scores(query.split())

        ranked = sorted(zip(scores, self.documents),

        key=lambda x: x[0],

        reverse=True

        )

        return [doc for _, doc in ranked[:k]]
    def dense_search(self,query: str,k: int = 10) -> List[Document]:
    """
    Dense Search using Qdrant.
    """

        logger.info(
        "Dense Search..."
        )

        return self.vector_service.similarity_search(
        query=query,
        k=k
        )
    def reciprocal_rank_fusion(self,dense_docs: List[Document],keyword_docs: List[Document],k: int = 60) -> List[Document]:
    """
    Merge Dense Search and BM25 results using
    Reciprocal Rank Fusion (RRF).
    """

        logger.info("Applying Reciprocal Rank Fusion...")

        scores = {}

        for rank, doc in enumerate(dense_docs):

            key = doc.page_content

            if key not in scores:

                scores[key] = {
                "document": doc,
                "score": 0
                }

            scores[key]["score"] += 1 / (k + rank + 1)

        for rank, doc in enumerate(keyword_docs):

            key = doc.page_content

            if key not in scores:

                scores[key] = {"document": doc,"score": 0}

        scores[key]["score"] += 1 / (k + rank + 1)

        ranked = sorted(scores.values(), key=lambda item: item["score"],reverse=True)

        logger.info("RRF returned %d documents.",len(ranked))

        return [item["document"]for item in ranked]
    def rerank(self,query: str,documents: List[Document],top_k: int = 5) -> List[Document]:
    """
    Re-rank retrieved documents using Cross Encoder.
    """

        logger.info("Re-ranking documents...")

        if not documents:
            return []

        pairs = [(query, doc.page_content)for doc in documents]

        scores = self.reranker.predict(pairs)

        ranked = sorted( zip(scores, documents),key=lambda item: item[0],reverse=True)

        return [doc for _, doc in ranked[:top_k]]

    def search(self,query: str,top_k: int = 5) -> List[Document]:
    """
    Complete Hybrid Search Pipeline.

    Steps:
        1. Dense Search
        2. BM25 Search
        3. Reciprocal Rank Fusion
        4. Cross Encoder Re-ranking
    """

        logger.info("=" * 50)
        logger.info("Hybrid Search Started")
        logger.info("Query: %s", query)

    # Step 1: Dense Search
        dense_results = self.dense_search(query=query,k=10)

    # Step 2: BM25 Search
        keyword_results = self.keyword_search(query=query,k=10)

    # Step 3: Merge Results
        merged_results = self.reciprocal_rank_fusion(dense_results=dense_results,keyword_docs=keyword_results)


    # Step 4: Re-rank Results
        final_results = self.rerank(query=query,documents=merged_results,top_k=top_k)

        logger.info(
        "Hybrid Search Finished (%d documents).",
        len(final_results)
        )

        logger.info("=" * 50)

        return final_results