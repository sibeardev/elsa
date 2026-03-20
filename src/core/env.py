from functools import cached_property

from pydantic import BaseModel, PostgresDsn, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseModel):
    USER: str
    PASSWORD: str
    DB: str
    HOST: str = "db"
    PORT: int = 5432
    URL: PostgresDsn | None = None

    @model_validator(mode="after")
    def assemble_url(self):
        if not self.URL:
            self.URL = (
                f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}"
                f"@{self.HOST}:{self.PORT}/{self.DB}"
            )
        return self


class EnvSettings(BaseSettings):
    POSTGRES: PostgresSettings
    DEBUG: bool = True
    API_KEY: SecretStr

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
