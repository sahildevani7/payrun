FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

ARG PAYRUN_REPO=https://github.com/sahildevani7/payrun.git
ARG PAYRUN_REF=base

RUN git clone --depth 1 --branch "$PAYRUN_REF" "$PAYRUN_REPO" /workspace \
    && rm -rf /workspace/.git

WORKDIR /workspace

RUN pip install --no-cache-dir -e ".[dev]"

CMD ["pytest", "-q"]
