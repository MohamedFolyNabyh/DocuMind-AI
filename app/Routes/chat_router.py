from fastapi import APIRouter, HTTPException

from app.schemas.tender_schema import (
    ChatRequest,
    ChatResponse
)

from app.agents.graph import graph

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post(
    "/",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest
):
    """
    Chat with Saudi Tender Agent.
    """

    try:

        result = graph.invoke({

            "session_id": request.session_id,

            "question": request.question

        })

        return ChatResponse(

            answer=result["answer"]

        )

    except Exception as ex:

        raise HTTPException(

            status_code=500,

            detail=str(ex)

        )