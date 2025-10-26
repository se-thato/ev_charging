from django.shortcuts import render, get_object_or_404, redirect
from ecommerce.models import Product
from .cart import Cart
from django.http import JsonResponse

def cart(request):
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_products()
    return render(request, 'Cart/cart_home.html', {'cart_products': cart_products})

"""
def add_to_cart(request, product_id):
    # Get the cart
    cart = Cart(request)
    # test for POST
    if request.POST.get('action') == 'post':
        # Get the product id
        product_id = int(request.POST.get('product_id'))
        
        # Get the product
        product = get_object_or_404(Product, id=product_id)

        # Add to cart/session
        cart.add(product=product)

        #Getting the quantity
        cart_quantity = cart.__len__()


        # Return success message
        #response = JsonResponse({'Product Name': product.name})
        response = JsonResponse({'success': True, 'qty': cart_quantity})
        return response
"""
def add_to_cart(request, product_id):
    # Get the cart
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        # Get the product id
        product = get_object_or_404(Product, id=product_id)
        

        # Add to cart/session
        cart.add(product=product)

        # Get quantity in cart
        cart_quantity = cart.__len__()



        # Return success JSON response
        #return JsonResponse({'Product Name': product.name})
        return JsonResponse({'success': True, 'qty': cart_quantity})
    
    

    # If request is not POST or no action, return a safe response
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


def cart_delete(request, product_id):
   pass

def cart_update(request, product_id):
   pass