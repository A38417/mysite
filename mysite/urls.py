from django.contrib import admin
from django.urls import path, include
from .views import login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', login_view, name='api-login'),
    path('', include('product.urls')),
]
