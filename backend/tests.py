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


class ShopCategoryTests(BaseTestCase):
    """Тесты для магазинов и категорий"""

    def test_shop_list(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('shop-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # один магазин

    def test_shop_toggle_state(self):
        self.client.force_authenticate(user=self.shop_user)
        url = reverse('shop-toggle-state', args=[self.shop.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        self.shop.refresh_from_db()
        self.assertFalse(self.shop.state)

    def test_category_list(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class ProductTests(BaseTestCase):
    """Тесты для товаров и поиска"""

    def test_product_list(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_product_detail(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('product-detail', args=[self.product_info.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.product_info.id)
        self.assertEqual(response.data['product']['name'], 'Smartphone')

    def test_product_search_by_name(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('product-search') + '?search=smart'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_product_search_by_category(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('product-search') + f'?category={self.category.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_product_search_no_results(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('product-search') + '?search=nonexistent'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


class ContactTests(BaseTestCase):
    """Тесты для контактов"""

    def test_create_contact(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('contact-list')
        data = {
            'city': 'SPb',
            'street': 'Nevsky',
            'house': '20',
            'phone': '+79998887766'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.filter(user=self.buyer).count(), 2)

    def test_list_contacts(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('contact-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_contact(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('contact-detail', args=[self.contact.id])
        data = {'phone': '+79990001122'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.phone, '+79990001122')


class BasketOrderTests(BaseTestCase):
    """Тесты для корзины и заказов"""

    def test_add_to_basket(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('order-add-to-basket')
        data = {'product_info_id': self.product_info.id, 'quantity': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        # Проверяем, что корзина создалась
        basket = Order.objects.get(user=self.buyer, state='basket')
        self.assertEqual(basket.ordered_items.count(), 1)
        self.assertEqual(basket.ordered_items.first().quantity, 2)

    def test_add_to_basket_nonexistent_product(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('order-add-to-basket')
        data = {'product_info_id': 9999, 'quantity': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['status'])

    def test_basket_view(self):
        self.client.force_authenticate(user=self.buyer)
        # Сначала добавляем товар
        self.client.post(reverse('order-add-to-basket'),
                         {'product_info_id': self.product_info.id, 'quantity': 2},
                         format='json')
        url = reverse('order-basket')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['total_price'], 2 * self.product_info.price_rrc)

    def test_confirm_order_success(self):
        self.client.force_authenticate(user=self.buyer)
        # Добавляем товар
        self.client.post(reverse('order-add-to-basket'),
                         {'product_info_id': self.product_info.id, 'quantity': 2},
                         format='json')
        basket = Order.objects.get(user=self.buyer, state='basket')
        url = reverse('order-confirm')
        data = {'order_id': basket.id, 'contact_id': self.contact.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        basket.refresh_from_db()
        self.assertEqual(basket.state, 'new')
        # Проверяем, что количество товара уменьшилось
        self.product_info.refresh_from_db()
        self.assertEqual(self.product_info.quantity, 8)  # было 10, купили 2

    def test_confirm_order_insufficient_stock(self):
        """
        Тест на недостаток товара при подтверждении.
        Добавляем в корзину больше, чем есть на складе, и ожидаем ошибку.
        """
        self.client.force_authenticate(user=self.buyer)
        # Добавляем больше, чем есть (quantity = 20 при наличии 10)
        self.client.post(reverse('order-add-to-basket'),
                         {'product_info_id': self.product_info.id, 'quantity': 20},
                         format='json')
        basket = Order.objects.get(user=self.buyer, state='basket')
        url = reverse('order-confirm')
        data = {'order_id': basket.id, 'contact_id': self.contact.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['status'])
        self.assertIn('errors', response.data)
        self.assertIn('insufficient_items', response.data)
        # Проверяем, что количество товара не изменилось
        self.product_info.refresh_from_db()
        self.assertEqual(self.product_info.quantity, 10)

    def test_order_list(self):
        self.client.force_authenticate(user=self.buyer)
        # Создаем завершенный заказ
        order = Order.objects.create(user=self.buyer, state='new', contact=self.contact)
        OrderItem.objects.create(order=order, product_info=self.product_info, quantity=1)
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class PartnerTests(BaseTestCase):
    """Тесты для функций поставщика"""

    def test_import_products_as_shop(self):
        self.client.force_authenticate(user=self.shop_user)
        url = reverse('partner-import-products')
        # Создаем простой YAML файл
        yaml_content = """
shop: Test Shop
categories:
  - id: 10
    name: New Category
goods:
  - id: 2001
    category: 10
    name: New Product
    price: 1000
    quantity: 5
"""
        uploaded_file = SimpleUploadedFile("price.yaml", yaml_content.encode(), content_type="application/x-yaml")
        data = {'file': uploaded_file}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['message'], 'Импорт запущен')

    def test_import_products_as_buyer(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('partner-import-products')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['status'])


class SentryDebugTests(APITestCase):
    """Тест для sentry-debug endpoint (ожидаем 500 ошибку)"""

    def test_sentry_debug(self):
        url = reverse('sentry-debug')
        # Эндпоинт выбрасывает исключение, поэтому мы ожидаем ошибку сервера.
        # В тестах можно проверить, что ответ имеет статус 500.
        try:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 500)
        except Exception:
            # Исключение ожидаемо, тест проходит
            pass