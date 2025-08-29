from django.shortcuts import render, redirect
from .models import Product
from django.contrib import messages
from django.http import HttpResponse



#Home page for ecommerce
def home_ecommerce(request):
    products = Product.objects.all()
    return render(request,'ecommerce/shop_home.html', {'products': products, 'show_categories': True,})


#Product details view
def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request,'ecommerce/product.html', {'product': product})


#Category view
def category(request, foo):
    # Replace hyphens with spaces in the category name
    foo = foo.replace('-', ' ')
    # This will fetch the category based on the name
    # and then filter products by that category.
    try:
        category = Product.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request,'ecommerce/category.html', {'products': products, 'category': category})
    except:
        messages.success(request, 'Category not found')
        return redirect('shop_home')


# --- Minimal placeholders for cart flow to satisfy URL imports ---

def cart(request):
    # This will display the cart contents
    return HttpResponse("Cart page (placeholder)")


def add_to_cart(request, product_id):
    # This will add the item to the cart
    messages.success(request, 'Added to cart.')
    return redirect('shop_home')


def remove_from_cart(request, product_id):
    # This will remove the item from the cart
    messages.info(request, 'Removed from cart.')
    return redirect('shop_home')


def checkout(request):
    # This will display the checkout page
    return HttpResponse("Checkout page (placeholder)")
