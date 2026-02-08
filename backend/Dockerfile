FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Устанавливаем git и системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Клонируем репозиторий вместо COPY
RUN git clone --branch main --depth 1 https://github.com/VadimMMR/product-agents-demo.git /tmp/repo

# Копируем только нужные файлы из клонированного репозитория
RUN cp /tmp/repo/backend/requirements.txt . && \
    pip install --no-cache-dir -r requirements.txt && \
    # Копируем backend
    cp -r /tmp/repo/backend/* . && \
    # Копируем generator (должна быть в корне репозитория)
    cp -r /tmp/repo/generator . || echo "Note: generator directory not found, continuing..." && \
    mkdir -p frontend && \
    cp -r /tmp/repo/frontend/* frontend/ && \
    rm -rf /tmp/repo  # Удаляем клонированный репозиторий

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]