FROM python:3.14-slim as builder

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv python pin 3.14 && \
    uv venv --python 3.14 /dep && \
    uv sync --no-dev
