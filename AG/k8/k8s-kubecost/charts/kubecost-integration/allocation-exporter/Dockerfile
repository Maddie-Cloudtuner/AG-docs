FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    prometheus-client==0.19.0 \
    requests==2.31.0

# Copy exporter script
COPY exporter.py /app/exporter.py

# Make script executable
RUN chmod +x /app/exporter.py

# Create non-root user for security
RUN useradd -r -u 1000 -s /bin/false exporter && \
    chown -R exporter:exporter /app

# Switch to non-root user
USER exporter

# Set Python unbuffered mode for proper logging
ENV PYTHONUNBUFFERED=1

# Expose metrics port
EXPOSE 9103

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:9103/metrics')" || exit 1

# Run exporter
ENTRYPOINT ["python3", "/app/exporter.py"]
