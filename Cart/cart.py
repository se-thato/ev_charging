from ecommerce.models import Product

class Cart():
    def __init__(self, request):
        self.session = request.session
        # Getting the current session key if it exists
        cart = self.session.get('session_key')
        # If no session key, create one
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # now making sure cart is available is available in all pages
        self.cart = cart


    def add(self, product, quantity=1):
        product_id = str(product.id)
        # Check if the product is already in the cart
        if product_id not in self.cart:
            self.cart[product_id] = {
                'price': str(product.price),
                'quantity': quantity
            }
        else:
            self.cart[product_id] = {'price': str(product.price)}
            
            # Increase quantity if it already exists
            self.cart[product_id]['quantity'] += 1

            self.session.modified = True


    def __len__(self):
        return len(self.cart)

        # Return total quantity of items in cart
        #return sum(item['quantity'] for item in self.cart.values())


    def get_products(self):
        products_ids = self.cart.keys()
        #use ids to get the product objects and add them to the cart
        products = Product.objects.filter(id__in=products_ids)
        return products