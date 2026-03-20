from fastapi import FastAPI

from app_factory import create_app
from core.config import settings

app: FastAPI = create_app(debug=settings.DEBUG)
