from .ecommerce import Cart


#creating context processor to make cart available in all templates
def cart_contents(request):
    #returning the default data from cart
    return {'cart': Cart(request)}