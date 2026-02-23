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

    def handle(self, *args, **options):
        """Основная логика команды"""
        # Беру данные из переменных окружения или использую значения по умолчанию
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')

        # Проверяю, есть ли уже суперпользователь
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                email=email,
                password=password,
                is_active=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Суперпользователь {email} успешно создан')
            )