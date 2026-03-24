# Django signals are a way to run code automatically when something happens.
# Like event listeners in JavaScript — "when X happens, run Y function".
#
# We use two signals here:
#   user_logged_in  → fires after a user successfully logs in
#   user_logged_out → fires just before a user's session is destroyed
#
# How cart will work with signals:
#
#   Login:
#     1. User logs in
#     2. Signal fires → we check if they have saved CartItems in the DB
#     3. We load those DB items into the session cart
#     4. User sees their previous cart restored
#
#   Logout:
#     1. User clicks logout
#     2. Signal fires → we save their current session cart to DB
#     3. Session is destroyed (cart data gone from session)
#     4. Next login → step 1 above restores it
#
#   Guest → Login:
#     If a guest added items before logging in,
#     we MERGE their guest session cart with their saved DB cart.
#     No items are lost.

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


@receiver(user_logged_in)
def restore_cart_on_login(sender, request, user, **kwargs):
    """
    Fires automatically after a user logs in.
    Loads their saved DB cart into the session so they see their previous items.
    Also merges any items they added as a guest before logging in.
    """
    from Cart.cart import Cart as SessionCart
    from ecommerce.models import Cart as DBCart, CartItem

    # Get the session cart — may have guest items in it already
    session_cart = SessionCart(request)

    # Look for an active DB cart for this user
    db_cart = DBCart.objects.filter(user=user, active=True).first()

    if not db_cart:
        # No saved cart — nothing to restore
        # But if they added items as a guest, save those to DB
        if session_cart.cart:
            _save_session_to_db(user, session_cart)
        return

    # Load DB cart items into the session cart
    # This merges DB items with any guest session items
    for item in db_cart.items.select_related('product').all():
        product = item.product
        product_id_str = str(product.id)

        if product_id_str in session_cart.cart:
            # Item exists in both session and DB — use the higher quantity
            # This prevents losing items added as guest
            existing_qty = session_cart.cart[product_id_str].get('quantity', 1)
            merged_qty = max(existing_qty, item.quantity)
            session_cart.cart[product_id_str]['quantity'] = merged_qty
        else:
            # Item only in DB — add it to session
            session_cart.cart[product_id_str] = {
                'price': str(product.price),
                'quantity': item.quantity,
            }

    # Save the merged cart back to session
    request.session['session_key'] = session_cart.cart
    request.session.modified = True

    # Also update DB cart to reflect merged quantities
    for product_id_str, data in session_cart.cart.items():
        try:
            product_id = int(product_id_str)
            cart_item = db_cart.items.filter(product_id=product_id).first()
            if cart_item:
                cart_item.quantity = data.get('quantity', 1)
                cart_item.save()
        except (ValueError, TypeError):
            pass


@receiver(user_logged_out)
def save_cart_on_logout(sender, request, user, **kwargs):
    """
    Fires automatically just before a user logs out.
    Saves their current session cart to the database so it's
    restored next time they log in.

    WHY user can be None:
    Django passes user=None if the session had already expired.
    We check for this before trying to save.
    """
    if user is None:
        # Session already expired — nothing to save
        return

    from Cart.cart import Cart as SessionCart

    session_cart = SessionCart(request)

    if not session_cart.cart:
        # Cart is empty — nothing to save
        return

    # Save session cart to database
    _save_session_to_db(user, session_cart)


def _save_session_to_db(user, session_cart):
    """
    Helper — saves a session cart to the database for a specific user.
    Used by both login (save guest items) and logout (save before session flush).
    """
    from ecommerce.models import Cart as DBCart, CartItem, Product

    # Get or create the user's active DB cart
    db_cart, _ = DBCart.objects.get_or_create(
        user=user,
        active=True,
        defaults={'country': None}
    )

    for product_id_str, data in session_cart.cart.items():
        try:
            product_id = int(product_id_str)
            product = Product.objects.get(id=product_id, active=True)
            quantity = data.get('quantity', 1)

            # update_or_create: if item already in DB cart, update quantity
            # if not, create it
            cart_item, created = CartItem.objects.get_or_create(
                cart=db_cart,
                product=product,
                defaults={
                    'quantity': quantity,
                    'price_at_time': product.price,
                }
            )

            if not created:
                # Item already exists — update quantity and price
                cart_item.quantity = quantity
                cart_item.price_at_time = product.price
                cart_item.save()

        except (ValueError, TypeError, Product.DoesNotExist):
            # Skip invalid product IDs or products that no longer exist
            pass