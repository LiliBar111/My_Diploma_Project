import os
from celery import Celery

# Указываю Django настройки для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')

# Создаю экземпляр Celery приложения
app = Celery('orders')

# Загружаю конфигурацию из Django settings с префиксом CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически нахожу и регистрирую задачи из всех приложений
app.autodiscover_tasks()