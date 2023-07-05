from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path

router = DefaultRouter()
router.register('products', views.ProductViewSet, basename='product')
router.register(r'orders', views.OrderViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
