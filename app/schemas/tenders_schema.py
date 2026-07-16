from pydantic import BaseModel,Field


class ChatRequest(BaseModel):
    session_id:str=Field(
        description='unique identity of session'
    )
    question:str=Field(
        description='user question',
        min_lenght=5,
        max_lenght=500
    )
    source:str

class ChatResponse(BaseModel):
    answer:str

    session_id:str

class UploadResponse(BaseModel):
    filename:str
    chunk:int
    status:str



class ErrorResponse(BaseModel):
    error:str
    details:str