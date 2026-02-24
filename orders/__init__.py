# Инициализирую Celery при старте Django
from .celery import app as celery_app

# Указываю какие объекты экспортировать при импорте *
__all__ = ('celery_app',)
