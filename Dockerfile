# =========================================
# Stage 1: Builder - bağımlılıkları kur
# =========================================
FROM python:3.11-slim AS builder

# Build sırasında pip cache yazmasın, daha hızlı ve temiz
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

# asyncpg gibi C extension'lı paketler için gerekli sistem araçları
# (slim imajda yok, manuel yüklüyoruz)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Önce sadece requirements.txt'i kopyala
# Sebep: Docker layer caching - kod değişse bile bağımlılıklar değişmediyse
# bu layer cache'ten gelir, build çok hızlanır
COPY requirements.txt .

# Bağımlılıkları kullanıcı dizinine kur (--user)
# Sonra bu klasörü runtime stage'e aktaracağız
RUN pip install --user --no-cache-dir -r requirements.txt

# =========================================
# Stage 2: Runtime - sadece çalışan kod
# =========================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/appuser/.local/bin:$PATH

# asyncpg runtime'da libpq'ya ihtiyaç duyar (kütüphane, dev paketleri değil)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Non-root kullanıcı oluştur (güvenlik)
# Container içinde root çalıştırmak production'da büyük güvenlik açığıdır
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 -m appuser

WORKDIR /app

# Builder stage'den yüklü paketleri kopyala
# --chown ile sahipliği appuser'a ver
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Uygulama kodunu kopyala
COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser ./alembic ./alembic
COPY --chown=appuser:appuser ./alembic.ini ./alembic.ini
COPY --chown=appuser:appuser ./entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

# Non-root user'a geç
USER appuser

EXPOSE 8000

# Healthcheck - Docker konteynerin sağlığını izlesin
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]