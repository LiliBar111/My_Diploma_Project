"""
Запуск: coverage run manage.py test backend
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Shop, Category, Product, ProductInfo, Contact, Order, OrderItem, Parameter, ProductParameter

User = get_user_model()


class BaseTestCase(APITestCase):
    """Базовый класс с общими setUp методами"""

    def setUp(self):
        # Создаем покупателя
        self.buyer = User.objects.create_user(
            email='buyer@example.com',
            password='buyerpass123',
            first_name='Buyer',
            last_name='User',
            type='buyer',
            is_active=True
        )
        # Создаем магазин (поставщика)
        self.shop_user = User.objects.create_user(
            email='shop@example.com',
            password='shoppass123',
            first_name='Shop',
            last_name='Owner',
            type='shop',
            is_active=True
        )
        self.shop = Shop.objects.create(
            name='Test Shop',
            user=self.shop_user,
            state=True
        )
        # Создаем категорию и связываем с магазином
        self.category = Category.objects.create(name='Electronics')
        self.category.shops.add(self.shop)
        # Создаем товар
        self.product = Product.objects.create(
            name='Smartphone',
            category=self.category
        )
        # Создаем информацию о товаре
        self.product_info = ProductInfo.objects.create(
            product=self.product,
            shop=self.shop,
            external_id=1001,
            quantity=10,
            price=50000,
            price_rrc=54990
        )
        # Добавим параметр
        param = Parameter.objects.create(name='Color')
        ProductParameter.objects.create(
            product_info=self.product_info,
            parameter=param,
            value='Black'
        )
        # Контакт для покупателя
        self.contact = Contact.objects.create(
            user=self.buyer,
            city='Moscow',
            street='Lenina',
            house='10',
            phone='+79991234567'
        )


class UserTests(BaseTestCase):
    """Тесты для регистрации, авторизации, профиля"""

    def test_register_user(self):
        url = reverse('user-register')
        data = {
            'email': 'new@example.com',
            'password': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'type': 'buyer'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['status'])
        self.assertEqual(User.objects.count(), 3)  # buyer, shop_user, new

    def test_register_password_mismatch(self):
        url = reverse('user-register')
        data = {
            'email': 'new@example.com',
            'password': 'newpass123',
            'password2': 'wrong',
            'first_name': 'New',
            'last_name': 'User',
            'type': 'buyer'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['status'])

    def test_login_success(self):
        url = reverse('user-login')
        data = {'email': 'buyer@example.com', 'password': 'buyerpass123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        self.assertIn('user', response.data)

    def test_login_failure(self):
        url = reverse('user-login')
        data = {'email': 'buyer@example.com', 'password': 'wrong'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['status'])

    def test_profile_authenticated(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'buyer@example.com')

    def test_profile_unauthenticated(self):
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('user-logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])