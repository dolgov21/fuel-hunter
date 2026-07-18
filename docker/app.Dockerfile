FROM python:3.14-slim AS builder

ENV UV_PROJECT_ENVIRONMENT=/venv

RUN pip install --no-cache-dir uv

WORKDIR /code

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.14-slim AS app

ENV PATH=/venv/bin:$PATH
ENV PYTHONPATH=/code:/venv
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY --from=builder /venv /venv

WORKDIR /code
COPY . .
