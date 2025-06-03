from django.shortcuts import render
from .models import Product


#Home page for ecommerce
def home_ecommerce(request):
    products = Product.objects.all()
    return render(request,'ecommerce/shop_home.html', {'products': products})


#Product details view
def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request,'ecommerce/product.html', {'product': product})
