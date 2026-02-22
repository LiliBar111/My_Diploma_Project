"""
Кастомная команда Django для создания суперпользователя.
Запускается автоматически при первом развертывании.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class Command(BaseCommand):
    """Команда для создания суперпользователя"""
    help = 'Создание суперпользователя из переменных окружения'