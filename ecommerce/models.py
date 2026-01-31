from django.db import models
from django.contrib.auth.models import User
#from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Profile(models.Model):
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    location = models.CharField(max_length=150, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    #This is for determining if the user is a station owner and can manage charging stations
    is_station_owner = models.BooleanField(default=False,help_text="Can this user manage charging stations?")
    #This indicates if the station owner has been verified by an admin
    is_station_owner_verified = models.BooleanField(default=False,help_text="Admin verified station owner")

    def __str__(self):
        return self.username
    

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5)  # SA, UK, US
    currency = models.CharField(max_length=10)  # ZAR,USD
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


#The supplier models the countries where suppliers operate
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True, help_text="Supplier support or sales email")
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, help_text="Country where the supplier operates")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    fulfillment_type = models.CharField(max_length=20,
        choices=[
            ('shopify', 'Shopify'),
            ('manual', 'Manual'),
            ('api', 'API'),
        ],
        default='manual',
        help_text="How orders are sent to the supplier"
    ) # This will define how orders are sent to the supplier

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

#The connector types available in different regions
class ConnectorType(models.Model):
    name = models.CharField(max_length=50)  # Type 2, CCS2, CHAdeMO
    region = models.CharField(max_length=50)  # EU, US, Asia

    def __str__(self):
        return self.name



class ShopifyStore(models.Model):
    shop_name = models.CharField(max_length=255, unique=True) # e.g., myshop.myshopify.com
    access_token = models.CharField(max_length=255, blank=True, null=True)
    scope = models.TextField(blank=True)
    installed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name


class Product(models.Model):
    # The supplier providing the product
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    # The country where the product is available
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # My selling price
    
    shopify_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    supplier_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    supplier_product_url = models.URLField(null=True, blank=True) # URL to the product on the supplier's site

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    compatible_connectors = models.ManyToManyField(ConnectorType)
    main_image = models.ImageField(upload_to='product_images/main/', blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def profit(self):
        if self.supplier_price:
            return self.price - self.supplier_price # So this is my profit margin
        return None

    def __str__(self):
        return self.name
    
    # So this will return the first image from the gallery if main_image is not set
    @property
    def main_image(self):
        first = self.gallery.first()
        if first:
            return first.image
        return None
    

#This model will store additional images for products, createsing a gallery for the product
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='product_images/gallery')
    alt_text = models.CharField(max_length=150, blank=True)
    is_primary = models.BooleanField(default=False, help_text="Mark true if this is the primary image for the product")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"



    # name = models.CharField(max_length=150)
    # description = models.TextField()
    # price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    # stock = models.PositiveIntegerField(default=0)
    # image = models.ImageField(upload_to='product_images/',  blank=True)
    # #sales
    # on_sale = models.BooleanField(default=False)
    # sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # def __str__(self):
    #     return self.name


# Store information about customers
class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("SHIPPED", "Shipped"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    shipping_address = models.TextField(null=True, blank=True)

    payment_reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"


    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    # products = models.ManyToManyField(Product, through='OrderItem')
    # total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # status = models.CharField(max_length=20, choices=[
    #     ('pending', 'Pending'),
    #     ('shipped', 'Shipped'),
    #     ('delivered', 'Delivered'),
    #     ('cancelled', 'Cancelled'),
    # ], default='pending')
    # customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    # created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    


class SupplierOrder(models.Model): # the supplier's order for a particular customer order
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    shipped = models.BooleanField(default=False)
    tracking_number = models.CharField(max_length=255, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"SupplierOrder #{self.id}"
    


# Address model to store customer addresses
# This can be used for shipping or billing addresses
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.zip_code}, {self.country}"


# Contains information about the cart
# A cart can have multiple products

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='carts')
    country = models.ForeignKey('Country', on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username} (Active: {self.active})"


    # Add an item to the cart
    def add_item(self, product, quantity=1):
        item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={'price_at_time': product.price}
        )
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        # This will always keep price snapshot up-to-date when adding new product
        item.price_at_time = product.price
        item.save()


    # Remove an item from the cart 
    def remove_item(self, product):
        CartItem.objects.filter(cart=self, product=product).delete()


    # Clear all items from the cart
    def clear_items(self):
        self.items.all().delete()


    # Total price of cart
    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())


    # Total quantity of items
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())


    # Convert cart into an Order
    def convert_to_order(self, shipping_address):
        #This will make sure only active carts can be converted
        if not self.active:
            raise ValueError("Cannot convert an inactive cart to order.")

        order = Order.objects.create(
            user=self.user,
            country=self.country,
            total_amount=self.total_price(),
            shipping_address=shipping_address
        )

        # Create OrderItems and SupplierOrders
        for item in self.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )
            # Create or get supplier order
            SupplierOrder.objects.get_or_create(
                supplier=item.product.supplier,
                order=order
            )

        # Mark cart as inactive
        self.active = False
        self.save()

        return order


    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    # products = models.ManyToManyField(Product, through='CartItem')
    # created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"Cart of {self.user.username}"
    # # This method allows adding items to the cart
    # # If the item already exists, it updates the quantity
    # def add_item(self, product, quantity=1):
    #     item, created = CartItem.objects.get_or_create(cart=self, product=product)
    #     if not created:
    #         item.quantity += quantity
    #     else:
    #         item.quantity = quantity
    #     item.save()
    # # This method allows removing items from the cart
    # # If the item does not exist, it does nothing
    # def remove_item(self, product):
    #     CartItem.objects.filter(cart=self, product=product).delete()
    # # This method clears all items from the cart
    # # It deletes all CartItem instances related to this cart
    # def clear_items(self):
    #     self.items.all().delete()
    

    # # This will dynamically calculate the total price of the cart
    # # and the total quantity of items in the cart
    # def total_price(self):
    #     return sum(item.product.price * item.quantity for item in self.items.all())

    # def total_quantity(self):
    #     return sum(item.quantity for item in self.items.all())
    


class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def subtotal(self):
        return self.price_at_time * self.quantity

    def supplier(self):
        return self.product.supplier

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"

    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['created_at']


# Cart item model to link products with the cart
# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)

#     def __str__(self):  
#         return f"{self.quantity} x {self.product.name} in cart"


# this model is used to store the wishlist of a user
# A wishlist can have multiple products
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist of {self.user.username}"
    # This method returns the total number of items in the wishlist
    # It counts the number of products linked to this wishlist    
    def total_items(self):
        return self.products.count()

    # Add a product to the wishlist
    def add_item(self, product):
        WishlistItem.objects.get_or_create(wishlist=self, product=product)

    # Remove a product from the wishlist
    def remove_item(self, product):
        WishlistItem.objects.filter(wishlist=self, product=product).delete()

    # Clear all products from the wishlist
    def clear_items(self):
        self.items.all().delete()



# Wishlist item model to link products with the wishlist
# This allows users to save products they are interested in for later
class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.user.username}'s wishlist"
    


# this model is used to store reviews for products
# A product can have multiple reviews from different users
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"
    
    class Meta:
        unique_together = ('product', 'user')  # Ensure a user can only review a product once
