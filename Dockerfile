FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN addgroup --system ecowatch && \
    adduser --system --ingroup ecowatch --home /app ecowatch

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create uploads directory and set permissions
RUN mkdir -p /app/uploads && \
    chown -R ecowatch:ecowatch /app

# Set home directory
ENV HOME=/app

# Switch to non-root user
USER ecowatch

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]