from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from ecommerce.models import Product
from .cart import Cart

from ecommerce.models import Cart as DBCart, CartItem


def add_to_cart(request, product_id):
    """
    Adds a product to the cart.
    - Always saves to session (works for guests too)
    - If user is logged in, also saves to database (visible in Django admin)
    """
    # Get the session-based cart
    session_cart = Cart(request)

    if request.POST.get('action') == 'post':
        # Get the product — 404 if not found or inactive
        product = get_object_or_404(Product, id=product_id)

        # Step 1: Add to session cart (works for everyone)
        session_cart.add(product=product)

        # Step 2: If user is logged in, also save to database
        if request.user.is_authenticated:
            _save_to_db_cart(request.user, product, quantity=1)

        # Return the updated cart quantity
        cart_quantity = session_cart.__len__()
        return JsonResponse({'success': True, 'qty': cart_quantity})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


def _save_to_db_cart(user, product, quantity=1):
    """
    Private helper — saves a cart item to the database.
    The underscore prefix means this is an internal function,
    not meant to be called from outside this file.

    Uses the Cart and CartItem models from ecommerce/models.py.
    These are the DATABASE models — different from the session-based Cart class.
    """

    # Get or create an active cart for this user
    # get_or_create returns (object, created_boolean)
    # We only want one active cart per user at a time
    db_cart, _ = DBCart.objects.get_or_create(
        user=user,
        active=True,
        defaults={'country': None}
    )

    # Use the Cart model's add_item method which handles
    # both creating new items and updating quantities
    db_cart.add_item(product, quantity=quantity)


def cart(request):
    """
    Displays the cart page.
    Reads from the session cart so both guests and logged-in users can see their items.
    """
    session_cart = Cart(request)
    cart_products = session_cart.get_products()
    return render(request, 'Cart/cart_home.html', {'cart_products': cart_products})


def cart_delete(request, product_id):
    """
    Removes a product from the cart.
    Removes from both session and database.
    """
    session_cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Step 1: Remove from session cart
    product_id_str = str(product_id)
    if product_id_str in session_cart.cart:
        del session_cart.cart[product_id_str]
        session_cart.session['session_key'] = session_cart.cart
        session_cart.session.modified = True

    # Step 2: Remove from database cart if user is logged in
    if request.user.is_authenticated:
        from ecommerce.models import Cart as DBCart, CartItem
        db_cart = DBCart.objects.filter(user=request.user, active=True).first()
        if db_cart:
            db_cart.remove_item(product)

    return JsonResponse({'success': True})


def cart_update(request, product_id):
    from .cart import Cart as SessionCart
    session_cart = SessionCart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
 
    # Update session cart
    product_id_str = str(product_id)
    if product_id_str in session_cart.cart:
        session_cart.cart[product_id_str]['quantity'] = quantity
        session_cart.session['session_key'] = session_cart.cart
        session_cart.session.modified = True
 
    # Update database cart if user is logged in
    if request.user.is_authenticated:
        from ecommerce.models import Cart as DBCart, CartItem
        db_cart = DBCart.objects.filter(user=request.user, active=True).first()
        if db_cart:
            item = CartItem.objects.filter(cart=db_cart, product=product).first()
            if item:
                item.quantity = quantity
                item.save()
 
    return JsonResponse({'success': True})