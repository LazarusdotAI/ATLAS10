# 🐳 A.T.L.A.S. Institutional-Grade Docker Configuration
# Multi-stage build for optimized production image

# ===== BUILD STAGE =====
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Add metadata labels
LABEL org.opencontainers.image.title="A.T.L.A.S. Trading System"
LABEL org.opencontainers.image.description="Advanced Trading & Learning Analysis System - Institutional Grade"
LABEL org.opencontainers.image.version=$VERSION
LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.revision=$VCS_REF
LABEL org.opencontainers.image.vendor="A.T.L.A.S. Development Team"
LABEL org.opencontainers.image.source="https://github.com/your-org/atlas-rebuilt"

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-prod.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-prod.txt

# ===== PRODUCTION STAGE =====
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r atlas && useradd -r -g atlas atlas

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/cache && \
    chown -R atlas:atlas /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER atlas

# Expose ports
EXPOSE 8000 8001

# Default command
CMD ["uvicorn", "atlas_server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ===== DEVELOPMENT STAGE =====
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-asyncio \
    black \
    flake8 \
    mypy \
    ipython \
    jupyter

# Install debugging tools
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    strace \
    && rm -rf /var/lib/apt/lists/*

# Switch back to atlas user
USER atlas

# Override command for development
CMD ["uvicorn", "atlas_server:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]

# ===== TESTING STAGE =====
FROM development as testing

# Switch to root for test setup
USER root

# Install additional testing tools
RUN pip install --no-cache-dir \
    pytest-benchmark \
    pytest-mock \
    pytest-xdist \
    coverage \
    bandit \
    safety

# Copy test configuration
COPY tests/ tests/
COPY pytest.ini .coveragerc ./

# Switch back to atlas user
USER atlas

# Run tests by default
CMD ["pytest", "tests/", "-v", "--cov=./", "--cov-report=html", "--cov-report=term"]
