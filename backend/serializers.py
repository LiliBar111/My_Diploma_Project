"""
Сериализаторы для преобразования моделей в JSON и обратно.
Определяю как данные будут представляться в API.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Shop, Category, Product, ProductInfo, Contact, Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра информации о пользователе"""
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'type')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации новых пользователей.
    Пароль не возвращается в ответе и проходит валидацию.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)  # Подтверждение пароля

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'type')

    def validate(self, attrs):
        """Проверяю что пароли совпадают"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        """Создаю пользователя, убирая поле подтверждения пароля"""
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class ContactSerializer(serializers.ModelSerializer):
    """Сериализатор для контактов пользователя"""
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'phone')

    def create(self, validated_data):
        """Автоматически привязываю контакт к текущему пользователю"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для позиции в заказе"""
    product_info = ProductInfoSerializer(read_only=True)
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'total_price')


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для заказа"""
    items = OrderItemSerializer(source='ordered_items', many=True, read_only=True)
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'dt', 'state', 'items', 'total_price')

    def create(self, validated_data):
        """Создаю заказ со статусом 'basket' для текущего пользователя"""
        validated_data['user'] = self.context['request'].user
        validated_data['state'] = 'basket'
        return super().create(validated_data)


class BasketSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины (специальный случай заказа)"""
    items = OrderItemSerializer(source='ordered_items', many=True, read_only=True)
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'items', 'total_price')