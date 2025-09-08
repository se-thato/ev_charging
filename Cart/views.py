from django.shortcuts import render

def cart(request):
    # This will display the cart contents
    return render(request, 'ecommerce/cart_home.html')


def add_to_cart(request, product_id):
   pass


def cart_delete(request, product_id):
   pass

def cart_update(request, product_id):
   pass