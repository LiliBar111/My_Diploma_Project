"""
Асинхронные задачи Celery.
Выполняются в фоновом режиме, не блокируя ответ пользователю.
"""
import yaml
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
import requests

from .models import Shop, Product, ProductInfo, Category, Order

logger = logging.getLogger(__name__)


@shared_task
def send_order_confirmation_email(order_id):
    """
    Асинхронная отправка подтверждения заказа на email.
    Запускается после подтверждения заказа, чтобы не задерживать ответ.
    """
    try:
        order = Order.objects.select_related('user').get(id=order_id)
        send_mail(
            f'Подтверждение заказа №{order.id}',
            'Ваш заказ подтвержден',
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )
    except Order.DoesNotExist:
        logger.error(f"Заказ {order_id} не найден")


@shared_task
def process_import_task(shop_id, url=None, file_content=None):
    """
    Асинхронный импорт товаров из YAML файла.
    Может занимать много времени, поэтому выполняю в фоне.
    """
    try:
        shop = Shop.objects.get(id=shop_id)

        # Загружаю данные из URL или из файла
        data = None
        if url:
            response = requests.get(url)
            data = yaml.safe_load(response.text)
        elif file_content:
            data = yaml.safe_load(file_content.decode('utf-8'))

        if not data:
            return

        # Использую транзакцию для целостности данных
        with transaction.atomic():
            # Удаляю старые товары этого магазина
            ProductInfo.objects.filter(shop=shop).delete()

            # Создаю новые товары из YAML
            for item in data.get('goods', []):
                product, _ = Product.objects.get_or_create(
                    name=item['name'],
                    defaults={'category_id': item['category']}
                )

                ProductInfo.objects.create(
                    product=product,
                    shop=shop,
                    external_id=item['id'],
                    quantity=item['quantity'],
                    price=item['price'],
                    price_rrc=item.get('price_rrc', item['price'])
                )

    except Exception as e:
        logger.error(f"Ошибка импорта: {str(e)}")