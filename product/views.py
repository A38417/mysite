from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from product.models import Product
from product.serializers import ProductSerializer


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
        fields = ['min_price', 'max_price']


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperUserOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [SearchFilter, OrderingFilter, filters.DjangoFilterBackend]
    filterset_class = ProductFilter
    filterset_fields = ['id', 'brand', 'type']
    search_fields = ['name']
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


