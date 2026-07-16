# from fastapi import APIRouter, File, UploadFile, HTTPException

# from app.core.container import (
#     pdf_service,
#     vector_service,
#     hybrid_service
# )

# router = APIRouter(
#     prefix="/upload",
#     tags=["Upload"]
# )


# @router.post("/")
# async def upload_pdf(file: UploadFile = File(...)):
#     """
#     Upload a tender PDF, process it,
#     generate embeddings and build BM25 index.
#     """

#     if not file.filename.lower().endswith(".pdf"):
#         raise HTTPException(
#             status_code=400,
#             detail="Only PDF files are allowed."
#         )

#     try:

#         pdf_bytes = await file.read()

#         documents = pdf_service.process_pdf(
#             pdf_bytes=pdf_bytes,
#             filename=file.filename
#         )

#         if not documents:
#             raise HTTPException(
#                 status_code=400,
#                 detail="No text found inside PDF."
#             )

#         vector_service.add_documents(documents)

#         hybrid_service.build_bm25(documents)

#         return {
#             "status": "success",
#             "filename": file.filename,
#             "chunks": len(documents),
#             "message": "PDF indexed successfully."
#         }

#     except Exception as ex:

#         raise HTTPException(
#             status_code=500,
#             detail=str(ex)
#         )

from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.core.container import (
    pdf_service,
    vector_service,
    hybrid_service,
)

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload PDF -> Extract Text -> Split -> Embed -> Store in Qdrant
    """

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    try:

        file_path = UPLOAD_DIR / file.filename

        contents = await file.read()

        with open(file_path, "wb") as f:
            f.write(contents)

        documents = pdf_service.process_pdf(
            str(file_path)
        )

        if len(documents) == 0:
            raise HTTPException(
                status_code=400,
                detail="No text found inside PDF."
            )

       

        vector_service.delete_source(file.filename)

        vector_service.add_documents(documents)

        hybrid_service.build_bm25(source=file.filename,documents=documents)

        return {
            "status": "success",
            "filename": file.filename,
            "chunks": len(documents),
            "message": "PDF indexed successfully."
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )