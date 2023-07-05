from rest_framework.serializers import ModelSerializer
from .models import Product, Order, OrderedProduct


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderedProductSerializer(ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderedProduct
        fields = '__all__'


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
