FROM python:3.11-slim

WORKDIR /app

RUN addgroup --system ecowatch && adduser --system --group ecowatch

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/

RUN mkdir -p uploads && chown -R ecowatch:ecowatch /app

USER ecowatch

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]