# Multi-stage Dockerfile for Simple Peptide Analyzer
# Optimized for both development and production use

# Build stage - install dependencies and run tests
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash module_user

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY backend/requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to module_user
RUN chown -R module_user:module_user /app

# Switch to non-root user
USER module_user

# Add user's local bin to PATH
ENV PATH=/home/module_user/.local/bin:$PATH

# Run tests during build (optional - can be disabled with --build-arg SKIP_TESTS=true)
ARG SKIP_TESTS=false
RUN if [ "$SKIP_TESTS" != "true" ] ; then \
    pip install --user pytest pytest-cov && \
    python -m pytest backend/tests/ -v ; \
    fi

# Production stage - minimal runtime image
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/module_user/.local/bin:$PATH

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (same as builder)
RUN useradd --create-home --shell /bin/bash module_user

# Set working directory
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /home/module_user/.local /home/module_user/.local

# Copy application code
COPY --chown=module_user:module_user backend/ backend/
COPY --chown=module_user:module_user examples/ examples/
COPY --chown=module_user:module_user manifest.json .
COPY --chown=module_user:module_user README.md .

# Switch to non-root user
USER module_user

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from backend.main import execute; result = execute({'peptide_sequences': ['TESTSEQ']}, {'job_id': 'health'}); exit(0 if result['status'] == 'success' else 1)"

# Default command - run the module with example data
CMD ["python", "backend/main.py"]

# Development stage - includes development tools
FROM builder as development

# Install development dependencies
RUN pip install --user --no-cache-dir \
    pytest>=7.0.0 \
    pytest-cov>=3.0.0 \
    pytest-mock>=3.6.0 \
    pytest-benchmark>=4.0.0 \
    black>=22.0.0 \
    isort>=5.10.0 \
    flake8>=4.0.0 \
    mypy>=0.910 \
    bandit>=1.7.0 \
    safety>=1.10.0 \
    ipython>=8.0.0 \
    jupyter>=1.0.0

# Copy development-specific files
COPY --chown=module_user:module_user Makefile .
COPY --chown=module_user:module_user .github/ .github/

# Expose port for Jupyter (if needed)
EXPOSE 8888

# Override default command for development
CMD ["/bin/bash"]

# Testing stage - optimized for CI/CD
FROM development as testing

# Set test environment variables
ENV PYTEST_ARGS="-v --cov=backend --cov-report=xml --cov-report=term"

# Run comprehensive tests
CMD ["sh", "-c", "python -m pytest backend/tests/ $PYTEST_ARGS && python backend/main.py"]

# Benchmarking stage - for performance testing
FROM development as benchmarking

# Install additional benchmarking tools
RUN pip install --user --no-cache-dir \
    memory_profiler>=0.60.0 \
    line_profiler>=3.5.0 \
    py-spy>=0.3.0

# Run performance benchmarks
CMD ["python", "-m", "pytest", "backend/tests/", "-v", "--benchmark-only", "--benchmark-json=benchmark_results.json"]

# Deployment stage - minimal image for AWS Lambda
FROM public.ecr.aws/lambda/python:3.11 as lambda-deployment

# Copy function code and dependencies
COPY backend/ ${LAMBDA_TASK_ROOT}/backend/
COPY examples/ ${LAMBDA_TASK_ROOT}/examples/
COPY manifest.json ${LAMBDA_TASK_ROOT}/

# Install dependencies
COPY backend/requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Set the CMD to your handler
CMD ["backend.main.execute"]