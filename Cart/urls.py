from django.urls import path
from . import views

app_name = 'Cart'

urlpatterns = [
    path('add/<int:product_id>/', views.add_to_cart, name='add-cart'),
    path('delete/<int:product_id>/', views.cart_delete, name='cart_delete'),
    path('update/<int:product_id>/', views.cart_update, name='cart_update'),
]