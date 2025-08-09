from pydantic import Field
from maleo_soma.dtos.settings import Settings as BaseSettings


class Settings(BaseSettings):
    ICD9_DB_PATH: str = Field(..., description="ICD10 Database Path")
    ICD10_DB_PATH: str = Field(..., description="ICD10 Database Path")
