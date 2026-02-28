from django.db import transaction
from django.db.models import Q, Prefetch
from django.contrib.auth import authenticate, login, logout
from rest_framework import status, generics, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend

from .models import User, Shop, Category, ProductInfo, Contact, Order, OrderItem
from .serializers import (
    UserSerializer, UserRegistrationSerializer, ShopSerializer,
    CategorySerializer, ProductInfoSerializer, ContactSerializer,
    OrderSerializer, BasketSerializer
)
from .tasks import send_order_confirmation_email, process_import_task


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
        username=request.data.get('email'),
        password=request.data.get('password')
    )

    if user and user.is_active:
        login(request, user)
        return Response({'status': True, 'user': UserSerializer(user).data})

    return Response({'status': False}, status=401)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Выход из системы"""
    logout(request)
    return Response({'status': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Получение профиля текущего пользователя"""
    return Response(UserSerializer(request.user).data)


# Тестовый endpoint для Sentry (выбрасывает исключение)
@api_view(['GET'])
@permission_classes([AllowAny])
def sentry_debug(request):
    raise Exception("Тестовое исключение для Sentry")


class ShopViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с магазинами"""
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]  # применяем тротлинг

    @action(detail=True, methods=['post'])
    def toggle_state(self, request, pk=None):
        """Включение/отключение приема заказов"""
        shop = self.get_object()
        shop.state = not shop.state
        shop.save()
        return Response({'status': True})


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с категориями"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]


class ProductInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet только для чтения информации о товарах.
    Создание и обновление только через импорт.
    """
    queryset = ProductInfo.objects.select_related('product', 'shop').prefetch_related('product_parameters__parameter').all()
    serializer_class = ProductInfoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['shop_id', 'product__category_id']
    search_fields = ['product__name']
    throttle_classes = [AnonRateThrottle, UserRateThrottle]  # для товаров можно и анонимам


class ContactViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с контактами пользователя"""
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """Возвращаю только контакты текущего пользователя"""
        return Contact.objects.filter(user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с заказами"""
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """Возвращаю заказы только текущего пользователя с оптимизацией запросов"""
        return Order.objects.filter(user=self.request.user).select_related('contact').prefetch_related(
            Prefetch('ordered_items', queryset=OrderItem.objects.select_related('product_info__product', 'product_info__shop'))
        )

    def get_serializer_class(self):
        """Выбираю сериализатор в зависимости от действия"""
        return BasketSerializer if self.action == 'basket' else OrderSerializer

    @action(detail=False, methods=['get'])
    def basket(self, request):
        """Получение корзины текущего пользователя"""
        basket, _ = Order.objects.get_or_create(user=request.user, state='basket')
        # Оптимизация для корзины
        basket = Order.objects.filter(id=basket.id).select_related('contact').prefetch_related(
            Prefetch('ordered_items', queryset=OrderItem.objects.select_related('product_info__product', 'product_info__shop'))
        ).first()
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
            return Response({'status': False}, status=404)

    @action(detail=False, methods=['post'])
    def confirm(self, request):
        """
        Подтверждение заказа.
        Теперь с проверкой наличия товара на складе.
        """
        try:
            with transaction.atomic():
                # Блокируем заказ и связанные товары для избежания гонок
                order = Order.objects.select_for_update().get(
                    id=request.data.get('order_id'),
                    user=request.user,
                    state='basket'
                )

                # Проверяем наличие всех товаров
                insufficient_items = []
                for item in order.ordered_items.select_related('product_info').all():
                    # Блокируем запись товара
                    product_info = ProductInfo.objects.select_for_update().get(id=item.product_info.id)
                    if product_info.quantity < item.quantity:
                        insufficient_items.append({
                            'product': product_info.product.name,
                            'available': product_info.quantity,
                            'requested': item.quantity
                        })

                if insufficient_items:
                    return Response({
                        'status': False,
                        'errors': 'Недостаточно товара на складе',
                        'insufficient_items': insufficient_items
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Списываем товары
                for item in order.ordered_items.all():
                    product_info = item.product_info
                    product_info.quantity -= item.quantity
                    product_info.save()

                # Меняем статус заказа
                order.state = 'new'
                order.save()

                # Асинхронно отправляем email
                send_order_confirmation_email.delay(order.id)
                return Response({'status': True})

        except Order.DoesNotExist:
            return Response({'status': False, 'errors': 'Заказ не найден'}, status=404)


class PartnerViewSet(viewsets.ViewSet):
    """ViewSet для функций поставщика"""
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    @action(detail=False, methods=['post'])
    def import_products(self, request):
        """Импорт товаров из YAML"""
        # Проверяю что пользователь - магазин
        if request.user.type != 'shop':
            return Response({'status': False}, status=403)

        shop = request.user.shop
        url = request.data.get('url')
        file = request.FILES.get('file')

        # Запускаю асинхронную задачу
        process_import_task.delay(shop.id, url, file.read() if file else None)
        return Response({'status': True, 'message': 'Импорт запущен'})


class ProductSearchView(generics.ListAPIView):
    """Расширенный поиск товаров с фильтрацией"""
    serializer_class = ProductInfoSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        """Применяю фильтры из запроса с оптимизацией"""
        queryset = ProductInfo.objects.filter(shop__state=True, quantity__gt=0).select_related('product', 'shop').prefetch_related('product_parameters__parameter')

        # Поиск по названию
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(product__name__icontains=search)

        # Фильтр по категории
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(product__category_id=category)

        return queryset.distinct()