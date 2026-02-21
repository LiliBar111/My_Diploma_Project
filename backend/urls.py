"""
Маршрутизация URL для API приложения.
Определяю все доступные endpoint'ы.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Создаю router для автоматической генерации URL
router = DefaultRouter()
router.register(r'shops', views.ShopViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductInfoViewSet)
router.register(r'partner', views.PartnerViewSet, basename='partner')

urlpatterns = [
    # Аутентификация
    path('user/register/', views.register_user),  # Регистрация
    path('user/login/', views.login_user),  # Вход
    path('user/logout/', views.logout_user),  # Выход
    path('user/profile/', views.user_profile),  # Профиль

    # Подключаю все маршруты от router
    path('', include(router.urls)),
]