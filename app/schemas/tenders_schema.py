from fastapi import BaseModel


class chatRequest(BaseModel):
    session_id:str=Field(
        description='unique identity of session'
    )
    request:str=Field(
        description='user question',
        min_lenght=5,
        max_lenght=500
    )

class ChatResponse(BaseModel):
    answer:str
    sources:list[str]
    session_id:str

class UploadResponse(BaseModel):
    filename:str
    chunk:int
    status:str



class ErrorResponse(BaseModel):
    error:str
    details:str