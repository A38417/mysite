from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from .models import Product, Order, OrderedProduct
from .serializers import ProductSerializer, OrderSerializer


class IsSuperUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return True

        return False


class ProductPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'pageSize'


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'brand', 'type']


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperUserOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [SearchFilter, OrderingFilter, filters.DjangoFilterBackend]
    filterset_class = ProductFilter
    # filterset_fields = ['id', 'brand', 'type']
    search_fields = ['name', 'brand']
    ordering_fields = '__all__'

    def list(self, request, *args, **kwargs):
        if 'query_all' in request.query_params:
            queryset = self.get_queryset()

            queryset = self.filter_queryset(queryset)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        type = request.data.get('type', None)
        brand = request.data.get('brand', None)

        TYPE_MAPPING = {
            '1': 'hot',
            '2': 'sale',
            '3': 'new',
        }

        BRAND_MAPPING = {
            '0': 'iphone',
            '1': 'samsung',
            '2': 'xiaomi',
            '3': 'redmi',
         }

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        product = serializer.instance
        product.type = TYPE_MAPPING[type]
        product.brand = BRAND_MAPPING[brand]
        product.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        type = request.data.get('type', None)
        brand = request.data.get('brand', None)

        TYPE_MAPPING = {
            '1': 'hot',
            '2': 'sale',
            '3': 'new',
        }

        BRAND_MAPPING = {
            '0': 'iphone',
            '1': 'samsung',
            '2': 'xiaomi',
            '3': 'redmi',
        }
        product = serializer.instance
        product.type = TYPE_MAPPING[type]
        product.brand = BRAND_MAPPING[brand]
        product.save()
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        total_price = 0

        ordered_products_data = request.data.pop('ordered_products')
        order_serializer = self.get_serializer(data=request.data)
        order_serializer.is_valid(raise_exception=True)
        order = order_serializer.save()

        for ordered_product_data in ordered_products_data:
            product_id = ordered_product_data.pop('product')
            quantity = ordered_product_data.pop('quantity')
            product = Product.objects.get(id=product_id)
            if int(product.quantity) == 0 or int(product.quantity) < quantity:
                raise ValidationError("Số lượng sản phẩm không hợp lệ")
            else:
                product.quantity -= quantity
                product.save()
                total_price += int(quantity) * int(product.price)
                OrderedProduct.objects.create(order=order, product=product, quantity=quantity)

        order.total_price = total_price
        order.save()

        headers = self.get_success_headers(order_serializer.data)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        data = []
        for item in serializer.data:
            ordered_products = OrderedProduct.objects.filter(order_id=item['id'])

            temp = {
                'products': [],
                'id': item['id'],
                'created_at': item['created_at'],
                'total_price': item['total_price'],
                'name': item['name'],
                'address': item['address'],
                'phone': item['phone'],
            }

            for ordered_product in ordered_products:
                product = Product.objects.get(id=ordered_product.product_id)
                temp['products'].append({
                    'name': product.name,
                    'price': product.price,
                    'type': product.type,
                    'brand': product.brand,
                    'quantity': ordered_product.quantity,
                })

            data.append(temp)
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        ordered_products = OrderedProduct.objects.filter(order_id=instance.id)

        data = {
            'products': [],
            'id': serializer.data['id'],
            'created_at': serializer.data['created_at'],
            'total_price': serializer.data['total_price'],
            'name': serializer.data['name'],
            'address': serializer.data['address'],
            'phone': serializer.data['phone'],
        }

        for ordered_product in ordered_products:
            product = Product.objects.get(id=ordered_product.product_id)
            data['products'].append({
                'name': product.name,
                'price': product.price,
                'type': product.type,
                'brand': product.brand,
                'quantity': ordered_product.quantity,
            })

        return Response(data)
