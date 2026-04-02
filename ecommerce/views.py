
import secrets
import hmac
import hashlib
import json

import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.db import models  # added for Sum aggregation

from .models import Category, Product, ShopifyStore, Cart, CartItem, Order, Supplier
from .storefront_client import create_cart, add_to_cart, remove_from_cart, get_cart
from Cart.cart import Cart as SessionCart


# ─────────────────────────────────────────────────────────────────────────────
# SHOP HOME
# ─────────────────────────────────────────────────────────────────────────────
def home_ecommerce(request):
    products = Product.objects.filter(active=True).select_related('category')

    for product in products:
        if product.on_sale and product.sale_price and product.price:
            discount = product.price - product.sale_price
            product.save_percent = round((discount / product.price) * 100)
        else:
            product.save_percent = None

    cart_count = _get_cart_count(request)
    categories = Category.objects.all()

    return render(request, 'ecommerce/shop_home.html', {
        'products': products,
        'categories': categories,
        'cart_count': cart_count,
        'show_categories': True,
    })


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT DETAIL
# ─────────────────────────────────────────────────────────────────────────────
def product(request, pk):
    product = get_object_or_404(Product, id=pk, active=True)
    cart_count = _get_cart_count(request)

    return render(request, 'ecommerce/product.html', {
        'product': product,
        'cart_count': cart_count,
    })


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY
# ─────────────────────────────────────────────────────────────────────────────
def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, active=True)
    cart_count = _get_cart_count(request)

    return render(request, 'ecommerce/category.html', {
        'category': category,
        'products': products,
        'cart_count': cart_count,
    })


# ─────────────────────────────────────────────────────────────────────────────
# SHOPIFY OAUTH — Step 1: redirect to Shopify permission screen
# ─────────────────────────────────────────────────────────────────────────────
def shopify_auth(request):
    shop = settings.SHOPIFY_SHOP_DOMAIN
    client_id = settings.SHOPIFY_CLIENT_ID
    redirect_uri = settings.SHOPIFY_REDIRECT_URI
    scopes = "read_products,write_products,read_orders,write_orders,read_inventory"

    state = secrets.token_urlsafe(16)
    request.session['oauth_state'] = state

    auth_url = (
        f"https://{shop}/admin/oauth/authorize"
        f"?client_id={client_id}"
        f"&scope={scopes}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
    )
    return redirect(auth_url)


# ─────────────────────────────────────────────────────────────────────────────
# SHOPIFY OAUTH CALLBACK — Step 2: exchange code for access token
# ─────────────────────────────────────────────────────────────────────────────
def shopify_callback(request):
    print("=== CALLBACK HIT ===")
    print("GET params:", dict(request.GET))

    shop = request.GET.get('shop')
    code = request.GET.get('code')
    hmac_received = request.GET.get('hmac')
    state_received = request.GET.get('state')

    print("shop:", shop)
    print("code:", code[:10] if code else None)
    print("state_received:", state_received)
    print("state_stored:", request.session.get('oauth_state'))

    if not all([shop, code, hmac_received, state_received]):
        print("=== FAILED: Missing parameters ===")
        return HttpResponseBadRequest("Missing required parameters")

    stored_state = request.session.get('oauth_state')
    if state_received != stored_state:
        print(f"=== FAILED: State mismatch === received:{state_received} stored:{stored_state}")
        return HttpResponseBadRequest("State mismatch — possible CSRF attack")

    query_params = request.GET.dict()
    query_params.pop('hmac', None)
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(query_params.items()))
    calculated_hmac = hmac.new(
        settings.SHOPIFY_CLIENT_SECRET.encode('utf-8'),
        sorted_params.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hmac, hmac_received):
        print("=== FAILED: HMAC mismatch ===")
        return HttpResponseBadRequest("Invalid HMAC — request may have been tampered with")

    print("=== SECURITY CHECKS PASSED ===")

    token_url = f"https://{shop}/admin/oauth/access_token"
    payload = {
        "client_id": settings.SHOPIFY_CLIENT_ID,
        "client_secret": settings.SHOPIFY_CLIENT_SECRET,
        "code": code,
    }

    response = requests.post(token_url, json=payload, timeout=10)
    data = response.json()
    print("Token response:", data)

    if "access_token" not in data:
        print("=== FAILED: No access token in response ===")
        return HttpResponseBadRequest(f"Failed to get access token: {data}")

    print("=== TOKEN RECEIVED SUCCESSFULLY ===")

    ShopifyStore.objects.update_or_create(
        shop_domain=shop,
        defaults={
            "access_token": data["access_token"],
            "scope": data.get("scope", ""),
        }
    )

    print("=== TOKEN SAVED TO DATABASE ===")

    del request.session['oauth_state']
    messages.success(request, f"Shopify store {shop} connected successfully!")
    return redirect('shop_home')


# ─────────────────────────────────────────────────────────────────────────────
# ADD TO CART (Storefront API — for Shopify checkout)
# Called when user clicks Add to Cart on shop_home or product page
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, active=True)

    if not product.shopify_variant_id:
        messages.error(request, "This product is not available for purchase yet.")
        return redirect('product', pk=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    # Add to local DB cart (for logged-in users) or session cart (for guests)
    if request.user.is_authenticated:
        # Get or create the user's active Cart first, then add/update the CartItem
        cart, _ = Cart.objects.get_or_create(user=request.user, active=True)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity, 'price_at_time': product.price}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.price_at_time = product.price  # refresh price snapshot
            cart_item.save()
    else:
        session_cart = SessionCart(request)
        session_cart.add(product, quantity)

    # Shopify Storefront API cart
    cart_id = request.session.get('shopify_cart_id')

    if cart_id:
        shopify_cart = add_to_cart(cart_id, product.shopify_variant_id, quantity)
    else:
        shopify_cart = create_cart(product.shopify_variant_id, quantity)

    if shopify_cart:
        request.session['shopify_cart_id'] = shopify_cart['cart_id']
        request.session['shopify_checkout_url'] = shopify_cart['checkout_url']
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'qty': _get_cart_count(request)})
        messages.success(request, f"'{product.name}' added to cart!")
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Could not add to Shopify cart'})
        messages.error(request, "Could not add item to cart. Please try again.")

    return redirect('product', pk=product_id)


# ─────────────────────────────────────────────────────────────────────────────
# CART VIEW — displays items from DB (if logged in) or session
# ─────────────────────────────────────────────────────────────────────────────
def cart_view(request):
    if request.user.is_authenticated:
        # Traverse Cart → CartItem using cart__user lookup
        cart_items = CartItem.objects.filter(
            cart__user=request.user,
            cart__active=True
        ).select_related('product')
        cart_products = [item.product for item in cart_items]
        cart_quantities = {item.product.id: item.quantity for item in cart_items}
        cart_total = sum(
            (item.price_at_time or item.product.price) * item.quantity
            for item in cart_items
        )
    else:
        # Guest: session cart
        session_cart = SessionCart(request)
        cart_products = session_cart.get_products()
        raw_cart = session_cart.cart
        cart_quantities = {int(k): v.get('quantity', 1) for k, v in raw_cart.items()}
        cart_total = sum(
            float(v.get('price', 0)) * v.get('quantity', 1)
            for v in raw_cart.values()
        )

    return render(request, 'ecommerce/cart.html', {
        'cart_products': cart_products,
        'cart_quantities': cart_quantities,
        'cart_quantities_json': json.dumps(cart_quantities),
        'cart_total': round(cart_total, 2),
    })


# ─────────────────────────────────────────────────────────────────────────────
# CART COUNT — lightweight endpoint for navbar badge
# Returns JSON: {"count": total_quantity}
# ─────────────────────────────────────────────────────────────────────────────
def cart_count_view(request):
    count = _get_cart_count(request)
    return JsonResponse({'count': count})


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE CART QUANTITY (called from AJAX)
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def cart_update(request, product_id):
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    product = get_object_or_404(Product, id=product_id, active=True)

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user, active=True)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity, 'price_at_time': product.price}
        )
        if not created:
            cart_item.quantity = quantity
            cart_item.save()
    else:
        session_cart = SessionCart(request)
        session_cart.add(product, quantity)

    return JsonResponse({'success': True})


# ─────────────────────────────────────────────────────────────────────────────
# REMOVE FROM CART (called from AJAX)
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def cart_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        # Filter through Cart → CartItem relationship
        CartItem.objects.filter(
            cart__user=request.user,
            cart__active=True,
            product=product
        ).delete()

    # Also remove from session cart
    session_cart = SessionCart(request)
    session_cart.remove(product)

    # Return updated total quantity
    total_qty = _get_cart_count(request)

    return JsonResponse({'success': True, 'qty': total_qty})


# ─────────────────────────────────────────────────────────────────────────────
# REMOVE FROM CART (Shopify Storefront API line removal)
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def remove_from_cart_view(request, line_id):
    cart_id = request.session.get('shopify_cart_id')

    if not cart_id:
        messages.error(request, "No active cart found.")
        return redirect('cart')

    from urllib.parse import unquote
    decoded_line_id = unquote(line_id)
    cart = remove_from_cart(cart_id, decoded_line_id)

    if cart:
        request.session['shopify_cart_id'] = cart['cart_id']
        messages.success(request, "Item removed from cart.")
    else:
        messages.error(request, "Could not remove item. Please try again.")

    return redirect('cart')


# ─────────────────────────────────────────────────────────────────────────────
# CHECKOUT — redirects to Shopify hosted checkout
# ─────────────────────────────────────────────────────────────────────────────
def checkout(request):
    checkout_url = request.session.get('shopify_checkout_url')

    if not checkout_url:
        messages.error(request, "Your cart is empty or has expired.")
        return redirect('shop_home')

    return redirect(checkout_url)


# ─────────────────────────────────────────────────────────────────────────────
# SHOPIFY WEBHOOK — receives real-time product updates from Shopify
# ─────────────────────────────────────────────────────────────────────────────
@csrf_exempt
@require_POST
def shopify_product_webhook(request):
    import base64

    shopify_hmac = request.headers.get('X-Shopify-Hmac-Sha256', '')
    body = request.body

    expected = base64.b64encode(
        hmac.new(
            settings.SHOPIFY_CLIENT_SECRET.encode('utf-8'),
            body,
            hashlib.sha256
        ).digest()
    ).decode('utf-8')

    if not hmac.compare_digest(expected, shopify_hmac):
        return HttpResponse("Unauthorized", status=401)

    try:
        sp = json.loads(body)
    except json.JSONDecodeError:
        return HttpResponse("Bad request", status=400)

    topic = request.headers.get('X-Shopify-Topic', '')

    if topic in ('products/create', 'products/update'):
        _sync_single_product(sp)
    elif topic == 'products/delete':
        shopify_gid = f"gid://shopify/Product/{sp.get('id')}"
        Product.objects.filter(shopify_id=shopify_gid).update(active=False)

    return HttpResponse("OK", status=200)


def _sync_single_product(sp):
    from .models import Supplier, Category

    category_name = sp.get("product_type") or "Uncategorized"
    category, _ = Category.objects.get_or_create(
        name=category_name,
        defaults={'slug': category_name.lower().replace(' ', '-')}
    )

    supplier_name = sp.get("vendor") or "Unknown Supplier"
    supplier, _ = Supplier.objects.get_or_create(name=supplier_name)

    variants = sp.get("variants", [])
    first_variant = variants[0] if variants else {}
    price = float(first_variant.get("price", 0))
    compare_at = first_variant.get("compare_at_price")
    on_sale = compare_at is not None and float(compare_at) > price
    raw_variant_id = first_variant.get("id")

    images = sp.get("images", [])
    image_url = images[0].get("src") if images else None
    shopify_gid = f"gid://shopify/Product/{sp.get('id')}"

    Product.objects.update_or_create(
        shopify_id=shopify_gid,
        defaults={
            "name": sp.get("title", ""),
            "description": sp.get("body_html") or "",
            "price": float(compare_at) if on_sale else price,
            "on_sale": on_sale,
            "sale_price": price if on_sale else None,
            "shopify_variant_id": f"gid://shopify/ProductVariant/{raw_variant_id}",
            "shopify_image_url": image_url,
            "supplier": supplier,
            "category": category,
            "active": (sp.get("status") == "active"),
        }
    )


# ─────────────────────────────────────────────────────────────────────────────
# HELPER — cart count for navbar badge
# ─────────────────────────────────────────────────────────────────────────────
def _get_cart_count(request):
    """
    Returns total cart quantity for the navbar badge.
    For logged-in users: queries DB via Cart → CartItem relationship.
    For guests: uses session cart.
    """
    if request.user.is_authenticated:
        total_qty = CartItem.objects.filter(
            cart__user=request.user,
            cart__active=True
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
        return total_qty
    else:
        session_cart = SessionCart(request)
        return len(session_cart)