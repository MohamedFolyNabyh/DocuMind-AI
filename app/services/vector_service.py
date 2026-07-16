import logging
import uuid
from typing import List

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from app.config.settings import settings

logger = logging.getLogger(__name__)


class VectorService:

    COLLECTION_NAME = "saudi_tenders"

    def __init__(self):

        logger.info("Initializing VectorService...")

        self.embedding_model = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        logger.info("Embedding model loaded successfully.")

        sample_vector = self.embedding_model.embed_query("hello world")
        self.embedding_dimension = len(sample_vector)

        logger.info(
            "Embedding Dimension = %d",
            self.embedding_dimension,
        )

        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None,
        )

        logger.info("Connected to Qdrant successfully.")

        self._create_collection_if_not_exists()

    # ---------------------------------------------------------

    def _create_collection_if_not_exists(self) -> None:

        try:

            collections = self.client.get_collections()

            existing = {
                collection.name
                for collection in collections.collections
            }

            if self.COLLECTION_NAME in existing:

                logger.info(
                    "Collection '%s' already exists.",
                    self.COLLECTION_NAME,
                )

                return

            logger.info(
                "Creating collection '%s'...",
                self.COLLECTION_NAME,
            )

            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.embedding_dimension,
                    distance=Distance.COSINE,
                ),
            )

            logger.info("Collection created successfully.")

        except UnexpectedResponse as ex:

            logger.exception(ex)

            raise

        except Exception as ex:

            logger.exception(ex)

            raise

    # ---------------------------------------------------------
    # Delete all chunks for one PDF
    # ---------------------------------------------------------

    def delete_source(self, source: str) -> None:

        self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="source",
                        match=MatchValue(value=source),
                    )
                ]
            ),
            wait=True,
        )

        logger.info(
            "Deleted all chunks for %s",
            source,
        )

    # ---------------------------------------------------------

    def add_documents(
        self,
        documents: List[Document],
    ) -> None:

        if not documents:

            logger.warning("No document to insert.")

            return

        logger.info(
            "Uploading %d documents...",
            len(documents),
        )

        points = []

        for doc in documents:

            vector = self.embedding_model.embed_query(
                doc.page_content
            )

            payload = {
                "content": doc.page_content,
                **doc.metadata,
            }

            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
            wait=True,
        )

        logger.info(
            "%d vectors uploaded successfully.",
            len(points),
        )

    # ---------------------------------------------------------

    def similarity_search(
        self,
        query: str,source,
        k: int = 5,
    ) -> List[Document]:

        logger.info("Searching for: %s", query)

        query_vector = self.embedding_model.embed_query(query)

        response = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            query_filter=Filter(
                must=[FieldCondition(
                        key="source",
                        match=MatchValue(
                            value=source
                        ),
                    )
                ]
            ),
            limit=k,
        )
           

        documents = []

        for point in response.points:

            payload = point.payload

            documents.append(
                Document(
                    page_content=payload.get("content", ""),
                    metadata={
                        key: value
                        for key, value in payload.items()
                        if key != "content"
                    },
                )
            )

        logger.info(
            "%d documents retrieved.",
            len(documents),
        )

        return documents

    # ---------------------------------------------------------

    def delete_collection(self,source:str) -> None:

        self.client.delete_collection(
            collection_name=self.COLLECTION_NAME
        )

        logger.info("Collection deleted.")

    # ---------------------------------------------------------

    def health_check(self) -> bool:

        try:

            self.client.get_collections()

            return True

        except Exception:

            return False