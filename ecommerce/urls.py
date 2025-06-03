from django.urls import path
from . import views


urlpatterns = [
    
    path('shop_home', views.home_ecommerce, name='shop_home'),
    path('products/<int:pk>/', views.product, name='products'),
   
]
