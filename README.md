# Сервис автоматизации закупок

Backend-приложение для автоматизации закупок в розничной сети. Разработано в рамках дипломного проекта.

## Содержание
- [Возможности](#возможности)
- [Технологии](#технологии)
- [Быстрый запуск через Docker](#быстрый-запуск-через-docker)
- [Локальный запуск](#локальный-запуск)
- [Новые возможности](#новые-возможности)
- [Тестирование и покрытие кода](#тестирование-и-покрытие-кода)
- [Полезные ссылки](#полезные-ссылки)

## Возможности

### Для покупателей:
- Регистрация, авторизация, восстановление пароля
- Подтверждение email при регистрации
- Просмотр товаров с фильтрацией по категориям, цене, параметрам
- Корзина (добавление/удаление товаров)
- Оформление и отслеживание заказов
- Управление контактами доставки
- Email-уведомления о статусе заказа

### Для поставщиков:
- Импорт товаров из YAML (по URL или загрузка файла)
- Включение/отключение приема заказов
- Просмотр заказов с своими товарами
- Обновление цен и количества

### Дополнительные улучшения
-  **Тротлинг** – ограничение частоты запросов для защиты от брутфорса
-  **Социальная аутентификация** – вход через Google и GitHub
-  **Улучшенная админка** – современный интерфейс с django-baton
-  **Изображения товаров и аватары** – загрузка и автоматическое создание миниатюр
-  **Sentry** – отслеживание ошибок в production
-  **Кэширование запросов** – ускорение ответов с помощью Redis
-  **Профилирование** – анализ производительности с django-silk
-  **Исправление N+1 запросов** – оптимизация работы с БД
-  **Проверка наличия товара** при подтверждении заказа (предотвращает отрицательные остатки)

## Технологии

- **Backend:** Python 3.10, Django 4.2, Django REST Framework
- **База данных:** PostgreSQL 15
- **Асинхронные задачи:** Celery 5.3, Redis 7
- **Контейнеризация:** Docker, Docker Compose
- **Веб-сервер:** Nginx, Gunicorn
- **Документация:** drf-yasg (Swagger/ReDoc)
- **Социальная аутентификация:** `social-auth-app-django`
- **Улучшенная админка:** `django-baton`
- **Изображения:** `easy-thumbnails`
- **Мониторинг ошибок:** `sentry-sdk`
- **Кэширование:** `django-cacheops`
- **Профилирование:** `django-silk`

## Быстрый запуск через Docker

### Требования
- Docker 20.10+ и Docker Compose 2.0+

#### 1. Клонируем репозиторий
git clone <url-репозитория>
cd orders

#### 2. Создаем .env файл из примера
cp .env.example .env

#### 3. Запускаем контейнеры
docker-compose up -d --build

#### 4. Применяем миграции
docker-compose exec web python manage.py migrate

#### 5. Создаем суперпользователя (автоматически из .env)
docker-compose exec web python manage.py initadmin

#### 6. Проверяем что все работает
docker-compose ps

### Доступные сервисы
Админка: http://localhost:8000/admin/ (admin@example.com / admin123)

API: http://localhost:8000/api/v1/

Документация Swagger: http://localhost:8000/swagger/

### Полезные команды Docker

#### Просмотр логов
docker-compose logs -f

#### Остановка
docker-compose down

#### Перезапуск конкретного сервиса
docker-compose restart web

#### Вход в контейнер
docker-compose exec web bash

#### Выполнение команд Django
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
Документация ReDoc: http://localhost:8000/redoc/

## Локальный запуск
### 1. Установка зависимостей
Python 3.10+, PostgreSQL, Redis
python -m venv venv

source venv/bin/activate  # Linux/Mac

**или**

venv\Scripts\activate  # Windows

pip install -r requirements.txt

### 2. Настройка базы данных
Создаем БД в PostgreSQL:

sudo -u postgres psql -c "CREATE DATABASE orders_db;"
sudo -u postgres psql -c "CREATE USER orders_user WITH PASSWORD 'orders_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE orders_db TO orders_user;"

### 3. Запуск

#### Применяем миграции
python manage.py migrate

#### Создаем суперпользователя
python manage.py createsuperuser

#### Запускаем сервер (в отдельном терминале)
python manage.py runserver

#### Запускаем Celery (в отдельном терминале)
celery -A orders worker --loglevel=info

## Новые возможности
#### Тротлинг (ограничение запросов)
Анонимные пользователи: не более 100 запросов в день
Авторизованные пользователи: не более 1000 запросов в день
При превышении лимита API возвращает статус 429 Too Many Requests.

#### Социальная аутентификация
Вход через Google и GitHub доступен по эндпоинтам:
/auth/login/google-oauth2/
/auth/login/github/

#### Улучшенная админ-панель (django-baton)
Современный интерфейс с выпадающими фильтрами, подтверждением несохранённых изменений, предпросмотром изображений и настраиваемым меню.

#### Загрузка изображений и миниатюры
Пользователи могут загружать аватары, товары – изображения. Автоматически создаются миниатюры (100x100 для аватаров, 200x200 для товаров).

#### Отслеживание ошибок через Sentry
Все необработанные исключения отправляются в Sentry. Тестовый эндпоинт:
GET /api/v1/sentry-debug/ (выбрасывает исключение для проверки).

#### Кэширование запросов (django-cacheops)
ProductInfo при получении одного объекта – кэш на 15 минут
Category и Shop – кэш на 1 час

#### Профилирование с django-silk
При DEBUG = True доступен интерфейс /silk/ для анализа запросов, SQL и времени выполнения.

#### Проверка наличия товара при подтверждении заказа
Заказ не будет подтверждён, если на складе недостаточно товара. Возвращается ошибка с деталями.

## Тестирование и покрытие кода

### Установка coverage (если ещё не установлен)
pip install coverage

### Запуск тестов с измерением покрытия
coverage run --source='backend' manage.py test backend

### Просмотр отчёта
coverage report

### Создание HTML отчёта
coverage html

## Полезные ссылки
*Админка: http://localhost:8000/admin/*

*API: http://localhost:8000/api/v1/*

*Swagger: http://localhost:8000/swagger/*

*ReDoc: http://localhost:8000/redoc/*
