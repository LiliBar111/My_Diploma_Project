"""
Маршрутизация URL для API приложения.
Определяю все доступные endpoint'ы.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Создаю router для автоматической генерации URL
router = DefaultRouter()
router.register(r'shops', views.ShopViewSet)  # /api/v1/shops/
router.register(r'categories', views.CategoryViewSet)  # /api/v1/categories/
router.register(r'products', views.ProductInfoViewSet)  # /api/v1/products/
router.register(r'contacts', views.ContactViewSet)  # /api/v1/contacts/
router.register(r'orders', views.OrderViewSet)  # /api/v1/orders/
router.register(r'partner', views.PartnerViewSet, basename='partner')  # /api/v1/partner/

urlpatterns = [
    # Аутентификация
    path('user/register/', views.register_user),  # Регистрация
    path('user/login/', views.login_user),  # Вход
    path('user/logout/', views.logout_user),  # Выход
    path('user/profile/', views.user_profile),  # Профиль

    # Поиск товаров с фильтрацией
    path('products/search/', views.ProductSearchView.as_view()),

    # Сброс пароля
    path('password-reset/', include('django_rest_passwordreset.urls')),

    # Подключаю все маршруты от router
    path('', include(router.urls)),
]