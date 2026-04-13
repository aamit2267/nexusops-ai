# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build tools for bcrypt and cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# Mirror structure for the install phase
COPY packages/ packages/
COPY services/auth-service/requirements.txt services/auth-service/

# Install directly to the system site-packages in the builder
RUN pip install --no-cache-dir -r services/auth-service/requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Copy the site-packages from the builder to the final image
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code and shared packages
COPY packages/ packages/
COPY services/auth-service/app/ services/auth-service/app/

# Environment setup
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Security: Non-root user
RUN useradd -m nexusops
USER nexusops

# Updated CMD to match the new PYTHONPATH and structure
CMD ["uvicorn", "services.auth-service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]