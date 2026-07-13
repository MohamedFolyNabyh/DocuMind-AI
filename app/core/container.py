"""
Application Services Container
"""

from app.services.pdf_service import PDFService
from app.services.vector_service import VectorService
from app.services.hybrid_search import HybridSearchService
from app.services.memory_service import MemoryService
from app.services.llm_service import LLMService

# ==========================
# Core Services
# ==========================

pdf_service = PDFService()

vector_service = VectorService()

memory_service = MemoryService()

llm_service = LLMService()

hybrid_service = HybridSearchService(
    vector_service=vector_service
)