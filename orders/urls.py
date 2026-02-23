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

urlpatterns = [
    # Админка Django
    path('admin/', admin.site.urls),

    # API моего приложения
    path('api/v1/', include('backend.urls')),

    # Документация API в двух форматах
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)