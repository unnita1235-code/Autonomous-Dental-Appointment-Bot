FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

COPY apps/api/requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install --prefix=/install --no-cache-dir -r /tmp/requirements.txt

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/local/bin:${PATH}"

WORKDIR /app

COPY --from=builder /install /usr/local
COPY apps/api /app

EXPOSE 8000

# Pre-flight config check runs at container start.
# Bypass with: docker run -e SKIP_CONFIG_CHECK=1 ...
CMD ["sh", "-c", "python -m app.simple"]
