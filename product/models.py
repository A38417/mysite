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