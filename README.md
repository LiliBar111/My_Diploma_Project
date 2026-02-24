# My_Diploma_Project

# Сервис автоматизации закупок

Backend-приложение для автоматизации закупок.

## Содержание
- [Возможности](#возможности)
- [Технологии](#технологии)
- [Быстрый запуск через Docker](#быстрый-запуск-через-docker)
- [Локальный запуск](#локальный-запуск)
- [Переменные окружения](#переменные-окружения)
- [API Endpoints](#api-endpoints)
- [Примеры запросов](#примеры-запросов)
- [Структура YAML для импорта](#структура-yaml-для-импорта)
- [Устранение проблем](#устранение-проблем)

## Возможности

### Для покупателей:
- Регистрация, авторизация, восстановление пароля
- Просмотр товаров с фильтрацией
- Корзина (добавление/удаление товаров)
- Оформление и отслеживание заказов
- Управление контактами доставки
- Email-уведомления о статусе заказа

### Для поставщиков:
- Импорт товаров из YAML (по URL или файл)
- Включение/отключение приема заказов
- Просмотр заказов с своими товарами
- Обновление цен и количества

## Технологии

- Python 3.10, Django 4.2, Django REST Framework
- PostgreSQL 15, Redis 7, Celery 5.3
- Docker, Docker Compose
- JWT аутентификация, Swagger документация

## Быстрый запуск через Docker

### Требования
- Docker 20.10+ и Docker Compose 2.0+

# Команды для запуска

## 1. Клонируем репозиторий
git clone <url-репозитория>
cd orders

## 2. Создаем .env файл
cp .env.example .env

## 3. Запускаем контейнеры
docker-compose up -d --build

## 4. Проверяем что все работает
docker-compose ps

## 5. Открываем в браузере
echo "Админка: http://localhost:8000/admin/"
echo "API: http://localhost:8000/api/v1/"
echo "Документация: http://localhost:8000/swagger/"

Данные для входа в админку:

Email: admin@example.com

Пароль: admin123

Полезные команды Docker

### Просмотр логов
docker-compose logs -f

### Остановка
docker-compose down

### Перезапуск конкретного сервиса
docker-compose restart web

### Вход в контейнер
docker-compose exec web bash

### Выполнение команд Django
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

Локальный запуск (без Docker)

1. Установка зависимостей

### Python 3.10+, PostgreSQL, Redis
python -m venv venv
source venv/bin/activate  # Linux/Mac

venv\Scripts\activate  # Windows

pip install -r requirements.txt

2. Настройка БД

### Создаем БД в PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE orders_db;"
sudo -u postgres psql -c "CREATE USER orders_user WITH PASSWORD 'orders_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE orders_db TO orders_user;"

3. Запуск
   
#3# Применяем миграции
python manage.py migrate

### Создаем суперпользователя
python manage.py createsuperuser

### Запускаем сервер (в отдельном терминале)
python manage.py runserver

### Запускаем Celery (в отдельном терминале)
celery -A orders worker --loglevel=info
Переменные окружения (файл .env)

### Обязательные
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

### База данных
DB_NAME=orders_db
DB_USER=orders_user
DB_PASSWORD=orders_password
DB_HOST=db           # для Docker: db, для локально: localhost
DB_PORT=5432

### Redis
REDIS_URL=redis://redis:6379/0  # для Docker
REDIS_URL=redis://localhost:6379/0  # для локально

### Email (для уведомлений)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@gmail.com

### Суперпользователь (создается автоматически)
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123
API Endpoints

### Аутентификация
POST	/api/v1/user/register/	Регистрация
POST	/api/v1/user/login/	Вход
POST	/api/v1/user/logout/	Выход
GET	/api/v1/user/profile/	Профиль
POST	/api/v1/password-reset/	Сброс пароля

### Товары
GET	/api/v1/products/	Список товаров
GET	/api/v1/products/search/?search=iPhone	Поиск
GET	/api/v1/categories/	Категории
GET	/api/v1/shops/	Магазины

### Корзина и заказы
GET	/api/v1/orders/basket/	Корзина
POST	/api/v1/orders/add_to_basket/	Добавить товар
POST	/api/v1/orders/remove_from_basket/	Удалить товар
POST	/api/v1/orders/confirm/	Подтвердить заказ
GET	/api/v1/orders/	Список заказов

### Контакты
GET	/api/v1/contacts/	Список контактов
POST	/api/v1/contacts/	Создать контакт
PUT	/api/v1/contacts/{id}/	Обновить
DELETE	/api/v1/contacts/{id}/	Удалить

### Для магазинов
GET	/api/v1/partner/orders/	Заказы магазина
POST	/api/v1/partner/import_products/	Импорт товаров
POST	/api/v1/partner/toggle_state/{id}/	Вкл/выкл заказы

## Примеры запросов

Регистрация
curl -X POST http://localhost:8000/api/v1/user/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "password2": "password123",
    "first_name": "Иван",
    "last_name": "Петров",
    "type": "buyer"
  }'
Авторизация

curl -X POST http://localhost:8000/api/v1/user/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
Добавление в корзину

curl -X POST http://localhost:8000/api/v1/orders/add_to_basket/ \
  -H "Cookie: sessionid=ваш-session-id" \
  -H "Content-Type: application/json" \
  -d '{
    "product_info_id": 1,
    "quantity": 2
  }'
Импорт товаров (для магазина)

## Через URL
curl -X POST http://localhost:8000/api/v1/partner/import_products/ \
  -H "Cookie: sessionid=ваш-session-id" \
  -F "url=https://example.com/price.yaml"

## Через файл
curl -X POST http://localhost:8000/api/v1/partner/import_products/ \
  -H "Cookie: sessionid=ваш-session-id" \
  -F "file=@price.yaml"
Структура YAML для импорта
yaml
shop: Название магазина

categories:
  - id: 1
    name: Электроника
  - id: 2
    name: Аксессуары

goods:
  - id: 1001
    category: 1
    name: Смартфон Samsung Galaxy S23
    price: 70000
    price_rrc: 74990
    quantity: 10
    parameters:
      Цвет: черный
      Память: 256GB
  
  - id: 1002
    category: 2
    name: Чехол силиконовый
    price: 500
    price_rrc: 990
    quantity: 50
    
Полезные ссылки
Админка: http://localhost:8000/admin/

API: http://localhost:8000/api/v1/

Swagger: http://localhost:8000/swagger/

ReDoc: http://localhost:8000/redoc/
