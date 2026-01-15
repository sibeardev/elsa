FROM python:3.14-slim
WORKDIR /src
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev
COPY src/ ./
ENV PYTHONUNBUFFERED=1