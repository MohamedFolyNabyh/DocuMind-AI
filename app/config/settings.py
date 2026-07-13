# from pydantic_settings import BaseSettings , SettingsConfigDict


# class settings(BaseSettings):
#     GEMINI_API_KEY:str
#     GEMINI_MODEL:str
#     QDRANT_URL:str
#     QDRANT_API_KEY:str
#     REDIS_PORT:int=6379
#     REDIS_HOST:int
#     REDIS_PASSWORD:str
#     REDIS_TTL:int=3600
#     EMBEDDING_MODEL:str
#     CROSS_ENCODER_MODEL:Str
#     CHUNK_SIZE:int
#     CHUNK_OVERLAP:int
#     TOP_K:int
#     LOG_LEVEL:str

#     model_config=SettingsConfigDict(
#         env_file='.env',
#         extra='ignore'
#     )


# settings=settings()    


from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    GEMINI_API_KEY: str

    GEMINI_MODEL: str

    QDRANT_URL: str

    QDRANT_API_KEY: str = ""

    COLLECTION_NAME: str

    EMBEDDING_MODEL: str

    REDIS_HOST: str

    REDIS_PORT: int

    REDIS_PASSWORD: str = ""

    CHUNK_SIZE: int

    CHUNK_OVERLAP: int

    class Config:
        env_file = ".env"


settings = Settings()