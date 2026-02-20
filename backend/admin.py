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

    # Поля при создании нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'type', 'is_active'),
        }),
    )


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    """Настройка отображения магазинов"""
    list_display = ('name', 'user', 'state')
    list_filter = ('state',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройка отображения категорий"""
    list_display = ('name',)
    # Для связи many-to-many использую горизонтальный фильтр
    filter_horizontal = ('shops',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Настройка отображения товаров"""
    list_display = ('name', 'category')


class ProductParameterInline(admin.TabularInline):
    """Встроенное редактирование параметров товара"""
    model = ProductParameter
    extra = 1  # Показывать 1 пустую форму для нового параметра


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    """Настройка отображения информации о товаре"""
    list_display = ('product', 'shop', 'price', 'quantity')
    # Добавляю возможность редактировать параметры прямо здесь
    inlines = [ProductParameterInline]


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    """Настройка отображения параметров"""
    list_display = ('name',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Настройка отображения контактов"""
    list_display = ('user', 'city', 'phone')


class OrderItemInline(admin.TabularInline):
    """Встроенное редактирование позиций заказа"""
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Настройка отображения заказов"""
    list_display = ('id', 'user', 'dt', 'state')
    list_filter = ('state', 'dt')
    inlines = [OrderItemInline]  # Показываю товары в заказе