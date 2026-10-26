
# Этап 1: установка зависимостей
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --prefix=/install \
    -r requirements.txt


# Этап 2: минимальный runtime-образ
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Переносим установленные зависимости из builder.
COPY --from=builder /install /usr/local

# Копируем приложение и конфигурацию миграций.
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini .

# Создаём непривилегированного пользователя.
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
