from django.db import transaction
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from rest_framework import status, generics, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import User, Shop, ProductInfo, Contact, Order, OrderItem
from .serializers import (
    UserSerializer, UserRegistrationSerializer, ShopSerializer,
    CategorySerializer, ProductInfoSerializer, ContactSerializer,
    OrderSerializer, BasketSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Регистрация нового пользователя"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'status': True}, status=201)
    return Response({'status': False, 'errors': serializer.errors}, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Авторизация пользователя"""
    user = authenticate(
        request,
        password=request.data.get('password')
    )

    if user and user.is_active:
        login(request, user)
        return Response({'status': True, 'user': UserSerializer(user).data})

    return Response({'status': False}, status=401)


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с заказами"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращаю заказы только текущего пользователя"""
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Выбираю сериализатор в зависимости от действия"""
        return BasketSerializer if self.action == 'basket' else OrderSerializer

    @action(detail=False, methods=['get'])
    def basket(self, request):
        """Получение корзины текущего пользователя"""
        basket, _ = Order.objects.get_or_create(user=request.user, state='basket')
        return Response(BasketSerializer(basket).data)

    @action(detail=False, methods=['post'])
    def add_to_basket(self, request):
        """Добавление товара в корзину"""
        try:
            product_info = ProductInfo.objects.get(id=request.data.get('product_info_id'))
            basket, _ = Order.objects.get_or_create(user=request.user, state='basket')

            item, created = OrderItem.objects.get_or_create(
                order=basket,
                product_info=product_info,
                defaults={'quantity': request.data.get('quantity', 1)}
            )

            if not created:
                item.quantity += int(request.data.get('quantity', 1))
                item.save()

            return Response({'status': True})
        except ProductInfo.DoesNotExist:
            return Response({'status': False}

    @action(detail=False, methods=['post'])
    def confirm(self, request):
        """Подтверждение заказа"""
        try:
            with transaction.atomic():  # Использую транзакцию для целостности
                order = Order.objects.get(
                    id=request.data.get('order_id'),
                    user=request.user,
                    state='basket'
                )

                order.state = 'new'
                order.save()

class PartnerViewSet(viewsets.ViewSet):
    """ViewSet для функций поставщика"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def import_products(self, request):
        """Импорт товаров из YAML"""
        if request.user.type != 'shop':
            return Response({'status': False}

        shop = request.user.shop
        url = request.data.get('url')
        file = request.FILES.get('file')

        # Запускаю асинхронную задачу
        process_import_task.delay(shop.id, url, file.read() if file else None)
        return Response({'status': True, 'message': 'Импорт запущен'})