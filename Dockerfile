FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml README.md /app/
COPY deploy_guard /app/deploy_guard
RUN pip install --upgrade pip && pip install .

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local /usr/local
ENTRYPOINT ["deploy-guard"]
