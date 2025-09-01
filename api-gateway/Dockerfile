# -------- auth-service/Dockerfile --------
FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Sistem bağımlılıkları (isteğe bağlı, gerekirse eklenir)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Railway'in verdiği PORT'u kullan; yoksa 8001
ENV PORT=8001
ENV HOST="::"

EXPOSE 8001

# IPv6 (dual-stack) bind + prod WSGI
CMD ["sh", "-c", "gunicorn -b [::]:${PORT:-8001} app:app --workers 2 --timeout 60"]
