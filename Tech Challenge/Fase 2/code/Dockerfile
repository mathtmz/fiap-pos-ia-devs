FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY outputs ./outputs

EXPOSE 8000

CMD ["sh", "-c", "uvicorn pcos_fase2.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
