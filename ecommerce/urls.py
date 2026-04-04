from django.urls import path
from . import views

urlpatterns = [

    #Shop pages

    # /shop_home  → shows all active products
    path('shop_home', views.home_ecommerce, name='shop_home'),

    # /product/5/ → shows product with id=5
    # <int:pk> captures the number from the URL and passes it to the view as 'pk'
    path('product/<int:pk>/', views.product, name='product'),

    # /category/ev-chargers/ → shows products in that category
    # <slug:slug> captures a slug (letters, numbers, hyphens) from the URL
    path('category/<slug:slug>/', views.category, name='category'),


    #Cart pages
    # /cart/ → shows the cart page
    path('cart/', views.cart_view, name='cart'),
    path('cart/count/', views.cart_count_view, name='cart_count'),

    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/delete/<int:product_id>/', views.cart_delete, name='cart_delete'),

    # /cart/add/5/ → adds product id=5 to cart (POST only — enforced by @require_POST)
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='cart_add'),

    # /cart/remove/gid%3A%2F%2F.../ → removes a line from the cart
    # <path:line_id> captures everything including slashes and special characters
    # We need <path:> not <str:> because Shopify line IDs contain forward slashes
    path('cart/remove/<path:line_id>/', views.remove_from_cart_view, name='cart_remove'),

    # /checkout/ → redirects user to Shopify's checkout page
    path('checkout/', views.checkout, name='checkout'),


    #Shopify OAuth

    # /shopify/auth/ → starts the OAuth flow (visit this in browser to connect store)
    path('shopify/auth/', views.shopify_auth, name='shopify_auth'),

    # /shopify/callback/ → Shopify redirects here after the owner approves
    path('shopify/callback/', views.shopify_callback, name='shopify_callback'),

    #Shopify Webhooks
    # /shopify/webhook/products/ → Shopify calls this when products change
    # Register this URL in Shopify Admin → Settings → Notifications → Webhooks
    path('shopify/webhook/products/', views.shopify_product_webhook, name='shopify_webhook_products'),

]
