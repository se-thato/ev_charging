from django.urls import path
from . import views

app_name = 'Cart'

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('delete/', views.cart_delete, name='cart_delete'),
    path('update/', views.cart_update, name='cart_update'),

]
