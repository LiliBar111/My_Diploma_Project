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
router.register(r'contacts', views.ContactViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'partner', views.PartnerViewSet, basename='partner')  # /api/v1/partner/

urlpatterns = [
    # Аутентификация
    path('user/register/', views.register_user),   
    path('user/login/', views.login_user),
    path('user/logout/', views.logout_user),
    path('user/profile/', views.user_profile),

    # Поиск товаров с фильтрацией
    path('products/search/', views.ProductSearchView.as_view()),

    # Сброс пароля (готовая библиотека)
    path('password-reset/', include('django_rest_passwordreset.urls')),

    # Тестовый endpoint для Sentry (выбрасывает исключение)
    path('sentry-debug/', views.sentry_debug, name='sentry-debug'),

    # Подключаю все маршруты от router
    path('', include(router.urls)),
]