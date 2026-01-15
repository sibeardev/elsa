from functools import cached_property

from pydantic import BaseModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseModel):
    USER: str
    PASSWORD: str
    DB: str
    HOST: str = "localhost"
    PORT: int = 5432
    URL: str | None = None

    @model_validator(mode="after")
    def assemble_url(cls, model):
        if not model.URL:
            model.URL = f"postgresql+asyncpg://{model.USER}:{model.PASSWORD}@{model.HOST}:{model.PORT}/{model.DB}"
        return model


class EnvSettings(BaseSettings):
    POSTGRES: PostgresSettings
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        validate_default=True,
        ignored_types=(cached_property,),
        extra="allow",
        use_attribute_docstrings=True,
    )
