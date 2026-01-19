import logging.config

from fastapi import FastAPI

from api.routes import organizations
from core import config

logging.config.dictConfig(config.LOGGING_CONFIG)


app = FastAPI(
    title="Organizations API",
    description="API приложение для справочника Организаций, Зданий, Деятельности.",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

app.include_router(organizations.router)
