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