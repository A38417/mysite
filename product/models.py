from django.db import models


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    type = models.CharField(max_length=10)
    price = models.BigIntegerField()
    quantity = models.IntegerField()
    img = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_total_price(self, quantity):
        return self.price * quantity


class Order(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.BigIntegerField(default=0)


class OrderedProduct(models.Model):
    order = models.ForeignKey(Order, related_name='ordered_products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
