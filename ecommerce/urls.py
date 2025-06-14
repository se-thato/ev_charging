from django.urls import path
from . import views


urlpatterns = [
    
    path('shop_home', views.home_ecommerce, name='shop_home'),
    path('product/<int:pk>/', views.product, name='product'),
    path('category/<str:foo>/', views.category, name='category'),
   
]
