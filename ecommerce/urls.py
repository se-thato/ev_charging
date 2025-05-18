from django.urls import path
from . import views


urlpatterns = [
    path('products/', views.product_list, name='products'),
    path('products/<int:pk>/', views.product_detail, name='product-detail'),
   
]
