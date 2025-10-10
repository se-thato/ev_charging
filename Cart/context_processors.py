from .cart import Cart

def cart_contents(request):
    cart = Cart(request)
    return {'cart': cart}
