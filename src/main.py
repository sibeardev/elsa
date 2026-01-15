import logging.config

from fastapi import FastAPI

from core import config

logging.config.dictConfig(config.LOGGING_CONFIG)


app = FastAPI()
