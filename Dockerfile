FROM python:3.14-slim
WORKDIR /opt
RUN pip install uv
COPY pyproject.toml uv.lock alembic.ini ./
RUN uv sync --no-dev
COPY . .
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/opt/src
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
