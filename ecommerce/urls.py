from django.urls import path
from . import views


urlpatterns = [
    
    path('shop_home', views.home_ecommerce, name='shop_home'),
    path('product/<int:pk>/', views.product, name='product'),
    path('category/<str:foo>/', views.category, name='category'),
    #path('cart/', views.cart, name='cart'),
    #path('cart-add/<int:product_id>/', views.add_to_cart, name='cart-add'),
    #path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
   
]
