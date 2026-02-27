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

# Типы пользователей в системе
USER_TYPE_CHOICES = [
    ('shop', 'Магазин'),  # Поставщик
    ('buyer', 'Покупатель'),  # Покупатель
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

    def create_user(self, email, password=None, **extra_fields):
        """Создание обычного пользователя"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Создание суперпользователя для админки"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Использую email вместо username для аутентификации.
    """
    REQUIRED_FIELDS = []  # Убираю обязательные поля кроме email и password
    objects = UserManager()

    # Email теперь уникальный и используется для входа
    USERNAME_FIELD = 'email'
    email = models.EmailField(unique=True)

    # Оставляю username для совместимости, но делаю необязательным
    username = models.CharField(max_length=150, blank=True)

    # Дополнительные поля для компании
    company = models.CharField(max_length=40, blank=True)
    position = models.CharField(max_length=40, blank=True)

    # Пользователь не активен до подтверждения email
    is_active = models.BooleanField(default=False)

    # Тип пользователя
    type = models.CharField(choices=USER_TYPE_CHOICES, max_length=5, default='buyer')

    # Добавляю поле для аватара
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Shop(models.Model):
    """Модель магазина/поставщика"""
    name = models.CharField(max_length=50)
    url = models.URLField(null=True, blank=True)  # Ссылка на прайс-лист
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    state = models.BooleanField(default=True)  # Включен ли прием заказов

    def __str__(self):
        return self.name


class Category(models.Model):
    """Категория товаров"""
    name = models.CharField(max_length=40)
    shops = models.ManyToManyField(Shop, related_name='categories', blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар"""
    name = models.CharField(max_length=80)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    """
    Информация о товаре от конкретного магазина.
    Здесь хранятся цены и количество.
    """
    model = models.CharField(max_length=80, blank=True)
    external_id = models.PositiveIntegerField()  # ID в системе поставщика
    product = models.ForeignKey(Product, related_name='product_infos', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, related_name='product_infos', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()  # Количество на складе
    price = models.PositiveIntegerField()  # Закупочная цена
    price_rrc = models.PositiveIntegerField()  # Розничная цена
    image = models.ImageField(upload_to='products/', null=True, blank=True)  # Добавляю изображение товара

    class Meta:
        # Гарантирую уникальность комбинации товар-магазин-внешнийID
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'], name='unique_product_info'),
        ]


class Parameter(models.Model):
    """Характеристика товара (цвет, размер и т.д.)"""
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    """Значение параметра для конкретного товара от конкретного магазина"""
    product_info = models.ForeignKey(ProductInfo, related_name='product_parameters', on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, related_name='product_parameters', on_delete=models.CASCADE)
    value = models.CharField(max_length=100)

    class Meta:
        # Один товар не может иметь два одинаковых параметра
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter'),
        ]


class Contact(models.Model):
    """Контактная информация пользователя для доставки"""
    user = models.ForeignKey(User, related_name='contacts', on_delete=models.CASCADE)
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=100)
    house = models.CharField(max_length=15)
    structure = models.CharField(max_length=15, blank=True)  # Корпус
    building = models.CharField(max_length=15, blank=True)  # Строение
    apartment = models.CharField(max_length=15, blank=True)  # Квартира
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.city}, {self.street} {self.house}'


class Order(models.Model):
    """Заказ"""
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)  # Дата создания
    state = models.CharField(choices=STATE_CHOICES, max_length=15, default='basket')
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('-dt',)  # Сортировка по дате (сначала новые)

    @property
    def total_price(self):
        """Вычисляемая сумма заказа"""
        return sum(item.total_price for item in self.ordered_items.all())


class OrderItem(models.Model):
    """Позиция в заказе"""
    order = models.ForeignKey(Order, related_name='ordered_items', on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo, related_name='ordered_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        # В одном заказе не может быть двух одинаковых товаров
        constraints = [
            models.UniqueConstraint(fields=['order', 'product_info'], name='unique_order_item'),
        ]

    @property
    def total_price(self):
        """Стоимость позиции"""
        return self.product_info.price_rrc * self.quantity


class ConfirmEmailToken(models.Model):
    """Токен для подтверждения email при регистрации"""

    @staticmethod
    def generate_key():
        """Генерирую уникальный токен"""
        return get_token_generator().generate_token()

    user = models.ForeignKey(User, related_name='confirm_email_tokens', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=64, db_index=True, unique=True)

    def save(self, *args, **kwargs):
        """При сохранении генерирую ключ если его нет"""
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)