"""
Главный файл маршрутизации URL.
Здесь я подключаю все URL-маршруты приложений.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Настройка генерации документации API
schema_view = get_schema_view(
    openapi.Info(
        title="API автоматизации закупок",
        default_version='v1',
        description="API для автоматизации закупок в розничной сети",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)