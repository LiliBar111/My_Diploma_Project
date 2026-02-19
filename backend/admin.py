"""
Настройка админ-панели Django.
Здесь я регистрирую модели и настраиваю их отображение.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Shop, Category, Product, ProductInfo,
    Parameter, ProductParameter, Contact, Order, OrderItem
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Настройка отображения пользователей в админке"""
    # Поля, отображаемые в списке пользователей
    list_display = ('email', 'first_name', 'last_name', 'type', 'is_active')
    # Фильтры справа
    list_filter = ('type', 'is_active')
    # Поля для поиска
    search_fields = ('email', 'first_name', 'last_name')

    # Разделение полей на группы при редактировании
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'company', 'position', 'type')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

