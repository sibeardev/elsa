import logging.config

from fastapi import FastAPI

from api.routes import health, organizations
from core import config
from core.exception_handlers import register_exception_handlers

logging.config.dictConfig(config.LOGGING_CONFIG)


app = FastAPI(
    title="Organizations API",
    description="API приложение для справочника Организаций, Зданий, Деятельности.",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

register_exception_handlers(app)

app.include_router(health.router)
app.include_router(organizations.router, prefix="/api")
