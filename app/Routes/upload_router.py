from fastapi import APIRouter, File, UploadFile, HTTPException

from app.core.container import (
    pdf_service,
    vector_service,
    hybrid_service
)

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a tender PDF, process it,
    generate embeddings and build BM25 index.
    """

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    try:

        pdf_bytes = await file.read()

        documents = pdf_service.process_pdf(
            pdf_bytes=pdf_bytes,
            filename=file.filename
        )

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No text found inside PDF."
            )

        vector_service.add_documents(documents)

        hybrid_service.build_bm25(documents)

        return {
            "status": "success",
            "filename": file.filename,
            "chunks": len(documents),
            "message": "PDF indexed successfully."
        }

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )