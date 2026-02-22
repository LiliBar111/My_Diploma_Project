# Использую официальный образ Python 3.10 - он легкий и стабильный
FROM python:3.10-slim

# Отключаю создание .pyc файлов и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаю рабочую директорию
WORKDIR /app

# Устанавливаю системные зависимости для работы с PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирую requirements.txt и устанавливаю зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копирую весь проект
COPY . /app/

# Создаю непривилегированного пользователя для безопасности
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Запускаю сервер (команда переопределяется в docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]