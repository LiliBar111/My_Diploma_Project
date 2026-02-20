"""
Сигналы Django для автоматических действий.
Срабатывают при определенных событиях в моделях.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django_rest_passwordreset.signals import reset_password_token_created
from .models import User, ConfirmEmailToken


@receiver(post_save, sender=User)
def create_confirm_token(sender, instance, created, **kwargs):
    """
    При создании нового пользователя создаю токен подтверждения email.
    Это срабатывает автоматически после сохранения пользователя.
    """
    if created and not instance.is_active:
        ConfirmEmailToken.objects.create(user=instance)