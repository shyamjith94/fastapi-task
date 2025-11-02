from typing import Any, Optional, Dict, ClassVar
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Fast Api 1.0.0"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Fast rest api"
    API_TAG: str = "/api"
    DEBUG: bool = False

  # data base
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER",)
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", )
    POSTGRES_PASSWORD: str = os.getenv(
        "POSTGRES_PASSWORD",)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", )
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    DATABASE_ECHO:bool = True # prod its false

    
    @field_validator("POSTGRES_PORT", mode="before")
    def validate_port(cls, v: Any) -> int:
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            return int(v.strip("'\""))  
        raise ValueError("Invalid port value")
    DATABASE_ECHO:bool = True

    # database url validator
    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def create_database_url(cls, v: Optional[str], info: dict) -> Optional[PostgresDsn]:
        if v is not None:
            return v
        values = info.data
        try:
            return PostgresDsn.build(
                scheme="postgresql",
                username=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                host=values.get("POSTGRES_SERVER"),
                path=values.get('POSTGRES_DB'),  # Don't add leading slash
                port=values.get("POSTGRES_PORT")
            )
        except ValueError:
            return None




    # Authentication settings
    ACCESS_TOKEN_EXPIRE: int = 24

    # Constants (not configurable via env)
    SECRET_KEY: ClassVar[str] = "j7D8QeUqD-5FZ5pPV8YrCytIbXoZxKnS0Nn9ScpKzJo"
    ALGORITHM: ClassVar[str] = "HS256"


    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    model_config = {
        "case_sensitive": True,
        "env_file": [".env.dev", ".env.prod"],  # Try both files, precedence to first one found
        "extra": "allow",
        "use_enum_values": True,
    }


settings = Settings()
