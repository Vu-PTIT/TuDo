# Stage 1: Build Rust PyO3 wheel
FROM rust:1.83-slim-bookworm AS rust-builder
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --break-system-packages maturin
WORKDIR /build/rust/image_core
COPY rust/image_core/ ./
RUN maturin build --release --out /dist

# Stage 2: Python Runtime
FROM python:3.12-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml ./
COPY --from=rust-builder /dist/*.whl /tmp/wheels/

RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache /tmp/wheels/*.whl && \
    uv pip install --no-cache -r pyproject.toml && \
    rm -rf /tmp/wheels

ENV PATH="/opt/venv/bin:$PATH"
COPY app/ ./app/
COPY scripts/ ./scripts/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

