FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Устанавливаем git и системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Клонируем репозиторий вместо COPY
RUN git clone --branch main --depth 1 https://github.com/VadimMMR/product-agents-demo.git /tmp/repo

# Копируем только нужные файлы
RUN cp /tmp/repo/agents/requirements.txt . && \
    pip install --no-cache-dir -r requirements.txt && \
    cp /tmp/repo/agents/main.py . && \
    rm -rf /tmp/repo  # Удаляем клонированный репозиторий

CMD ["python", "main.py"]