from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Profile(models.Model):
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    location = models.CharField(max_length=150, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images/',  blank=True)
    #sales
    on_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


# Store information about customers
class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, through='OrderItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    products = models.ManyToManyField(Product, through='CartItem')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"
    # This method allows adding items to the cart
    # If the item already exists, it updates the quantity
    def add_item(self, product, quantity=1):
        item, created = CartItem.objects.get_or_create(cart=self, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
    # This method allows removing items from the cart
    # If the item does not exist, it does nothing
    def remove_item(self, product):
        CartItem.objects.filter(cart=self, product=product).delete()
    # This method clears all items from the cart
    # It deletes all CartItem instances related to this cart
    def clear_items(self):
        self.items.all().delete()
    

    # This will dynamically calculate the total price of the cart
    # and the total quantity of items in the cart
    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())
    


# Cart item model to link products with the cart
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):  
        return f"{self.quantity} x {self.product.name} in cart"


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
