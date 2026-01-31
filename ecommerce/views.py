from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Product
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
import secrets, requests, hmac, hashlib
from django.conf import settings
from .models import ShopifyStore


#Home page for ecommerce
def home_ecommerce(request):
    products = Product.objects.filter(active=True) # This will fetch only active products
    # Category model doesn't have `active` or `parent` fields; fetch all categories instead
    categories = Category.objects.all()

    return render(request,'ecommerce/shop_home.html',{
            'products': products,
            'categories': categories,
            'show_categories': True,
        }
    )


# def home_ecommerce(request):
#     products = Product.objects.all()

#     return render(request,'ecommerce/shop_home.html', {'products': products, 'show_categories': True,})


#This will handle Shopify OAuth authentication
def shopify_auth(request):
    shop = "volt-hub-dev.myshopify.com"  # your dev store
    client_id = settings.SHOPIFY_CLIENT_ID
    redirect_uri = settings.SHOPIFY_REDIRECT_URI
    scopes = "read_products,write_products" # Setting up scopes, adjust as needed, separated by commas
    state = secrets.token_urlsafe(16)  # random string for security

    request.session['oauth_state'] = state

    # This auth_url will redirect user to Shopify's OAuth page
    auth_url = f"https://{shop}/admin/oauth/authorize?client_id={client_id}&scope={scopes}&redirect_uri={redirect_uri}&state={state}"
    return redirect(auth_url)



# This function will handle the callback from Shopify after user authorizes the app
# It will exchange the code for an access token, and save it in the database
def shopify_callback(request):
    # 1. Get query parameters from Shopify
    shop = request.GET.get('shop')
    code = request.GET.get('code')
    hmac_received = request.GET.get('hmac') # HMAC for verifying request authenticity

    if not shop or not code or not hmac_received:
        return HttpResponseBadRequest("Missing required parameters")

    # 2. Verify request authenticity (HMAC)
    query_params = request.GET.dict()
    query_params.pop('hmac')

    sorted_params = "&".join(
        f"{k}={v}" for k, v in sorted(query_params.items()) #This will sort the parameters
    )

    #This will calculate HMAC using the client secret, and compare with received HMAC
    calculated_hmac = hmac.new(
        settings.SHOPIFY_CLIENT_SECRET.encode(),
        sorted_params.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hmac, hmac_received): # If HMACs don't match, reject the request
        return HttpResponseBadRequest("Invalid HMAC")

    # 3. Exchange code for access token
    token_url = f"https://{shop}/admin/oauth/access_token"

    payload = {
        "client_id": settings.SHOPIFY_CLIENT_ID,
        "client_secret": settings.SHOPIFY_CLIENT_SECRET,
        "code": code,
    }

    response = requests.post(token_url, json=payload)
    data = response.json()

    if "access_token" not in data:
        return HttpResponseBadRequest("Failed to get access token")

    access_token = data["access_token"]

    # 4. Save token to database
    # Prevent duplicate entries by updating existing store or creating new one
    ShopifyStore.objects.update_or_create(
        shop_domain=shop,
        defaults={"access_token": access_token},
    )

    return HttpResponse("Shopify store connected successfully")





#Product details view
def product(request, pk):
    #product = Product.objects.get(id=pk)
    product = get_object_or_404(Product, id=pk, active=True) # this will ensure only active products are fetched
    return render(request,'ecommerce/product.html', {'product': product})


#Category view

def category(request, slug):
    category = get_object_or_404(Category, slug=slug, active=True) # Ensure the category is active
    products = Product.objects.filter(category=category, active=True) # This will fetch only active products in the category

    return render(request,'ecommerce/category.html',{
            'category': category,
            'products': products
        }
    )


# def category(request, foo):
#     # Replace hyphens with spaces in the category name
#     foo = foo.replace('-', ' ')
#     # This will fetch the category based on the name
#     # and then filter products by that category.
#     try:
#         category = Product.objects.get(name=foo)
#         products = Product.objects.filter(category=category)
#         return render(request,'ecommerce/category.html', {'products': products, 'category': category})
#     except:
#         messages.success(request, 'Category not found')
#         return redirect('shop_home')





#Cart Section






def checkout(request):
    # This will display the checkout page
    return HttpResponse("Checkout page (placeholder)")
