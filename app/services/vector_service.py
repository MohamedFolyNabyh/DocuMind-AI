import logging
from typing import List
import uuid

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore  # تم تصحيح الاسم 💡
from qdrant_client import QdrantClient 
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams, PointStruct

from app.config.settings import settings
from qdrant_client.models import PointStruct
logger = logging.getLogger(__name__)

class VectorService:
    # تم توحيد الاسم بحرف N في الآخر
    COLLECTION_NAME = "saudi_tenders"
    
    def __init__(self):
        logger.info("Initializing VectorService...")

        # 1. Load embedding model
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        logger.info("Embedding model loaded successfully.")

        # 2. حساب المقاس ديناميكياً (حركة ذكية وتم تصحيح اسم الدالة)
        sample_vector = self.embedding_model.embed_query("hello world")
        self.embedding_dimension = len(sample_vector)  # توحيد اسم المتغير هنا

        logger.info("Embedding Dimension = %d", self.embedding_dimension)

        # 3. Create Qdrant Client
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None
        )
        logger.info("Connected to Qdrant successfully.")
        
        # 4. تشغيل دالة الفحص التلقائي فور قيام السيرفر
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self) -> None:  # تصحيح صيغة الدالة والمسافات 🛠️
        """
        Create collection if it doesn't already exist.
        """
        try:
            collections = self.client.get_collections()
            existing = {collection.name for collection in collections.collections}
            
            if self.COLLECTION_NAME in existing:
                logger.info("Collection '%s' already exists.", self.COLLECTION_NAME)
                return  # الخروج الآمن هنا

            logger.info("Creating collection '%s'...", self.COLLECTION_NAME)
            
            # تم تصحيح البارامتر ليكون vectors_config بالجمع
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.embedding_dimension,
                    distance=Distance.COSINE
                )
            )
            logger.info("Collection '%s' created successfully.", self.COLLECTION_NAME)
            
        except UnexpectedResponse as ex:
            logger.exception("Qdrant unexpected response error: %s", ex)
            raise
        except Exception as ex:
            logger.exception("Failed to handle collection check/creation: %s", ex)
            raise
    def add_documents(self,documents:list[Document]) ->None:
        if not documents:
            logger.warning("No document to insert")
            return
        logger.info("documents '%d'",
        len(documents)
        )
        points=[]

        for doc in documents:
            vector=self.embedding_model.embed_query(doc.page_content)
            payload={
                'content':doc.page_content,
                **doc.metadata
            }
            point=PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload
            )
            points.append(point)
        logger.info("upload %d vector",
        len(points)
        )
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
            wait=True
        )
        logger.info('Documents inserted successfully')
    def similarty_search(self,query:str,k:int=5) ->List[Document]:
        logger.info('searching for : %s',query)
        query_vector=self.embedding_model.embed_query(
            query
        )
        response=self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            limit=k
        )
        documents=[]
        for point in response.points:
            payload=point.payload
            document=Document(
                page_content=payload.get("content",""),
                metadata={key:value for key,value in payload.items if key!="content" }
            )
            documents.append(document)
        logger.info("%d documents retrieved",
        len(documents))
        return documents

    def delete_collection(self) -> None:
    """
    Delete the collection.
    """

    self.client.delete_collection(
        collection_name=self.COLLECTION_NAME
    )

    logger.info("Collection deleted.")
    def health_check(self) -> bool:

    try:

        self.client.get_collections()

        return True

    except Exception:

        return False