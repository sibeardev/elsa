FROM python:3.14-slim
WORKDIR /opt
RUN pip install uv
COPY pyproject.toml uv.lock alembic.ini ./
RUN uv sync --no-dev
COPY src/ src/
COPY scripts/ scripts/
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/opt/src