import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    def _database_error_response(request: Request, exc: BaseException) -> JSONResponse:
        logger.exception(
            "Database error on %s %s: %s",
            request.method,
            request.url.path,
            exc,
        )
        return JSONResponse(status_code=500, content={"detail": "Database error"})

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        return _database_error_response(request, exc)

    @app.exception_handler(OSError)
    async def os_error_handler(request: Request, exc: OSError) -> JSONResponse:
        return _database_error_response(request, exc)
