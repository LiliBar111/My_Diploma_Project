"""
Модели данных для сервиса закупок.
Определяю структуру базы данных и связи между таблицами.
"""
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django_rest_passwordreset.tokens import get_token_generator

# Константы для выбора статуса заказа
STATE_CHOICES = [
    ('basket', 'Корзина'),  # Товары в корзине, еще не заказ
    ('new', 'Новый'),  # Новый заказ
    ('confirmed', 'Подтвержден'),  # Подтвержден покупателем
    ('assembled', 'Собран'),  # Собран на складе
    ('sent', 'Отправлен'),  # Отправлен покупателю
    ('delivered', 'Доставлен'),  # Доставлен
    ('canceled', 'Отменен'),  # Отменен
]

class UserManager(BaseUserManager):
    """
    Менеджер для создания пользователей.
    Переопределяю стандартный менеджер для работы с email как основным полем.
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Базовый метод создания пользователя"""
        if not email:
            raise ValueError('Email должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

