import logging.config

from fastapi import FastAPI

from api.routes import organizations
from core import config

logging.config.dictConfig(config.LOGGING_CONFIG)


app = FastAPI()

app.include_router(organizations.router)
