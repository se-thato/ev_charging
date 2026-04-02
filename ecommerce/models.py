from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator



# PROFILE
# Extends Django's built-in User model with extra fields.
# We use a OneToOneField so each User has exactly one Profile.
class Profile(models.Model):
    # OneToOneField means: one User → one Profile, and one Profile → one User.
    # on_delete=models.CASCADE means: if the User is deleted, delete the Profile too.
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True,blank=True, related_name='profile')

    # null=True  → the database column can store NULL (no value)
    # blank=True → Django forms won't require this field
    # Both are needed together for optional fields
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    location = models.CharField(max_length=150, null=True, blank=True)

    # ImageField stores the file path in the DB, not the image itself.
    # upload_to sets the subfolder inside your MEDIA_ROOT directory.
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    # BooleanField stores True or False.
    # help_text appears in the Django admin interface as a hint.
    is_station_owner = models.BooleanField(default=False,help_text="Can this user manage charging stations?")
    is_station_owner_verified = models.BooleanField(default=False,help_text="Admin verified station owner")

    def __str__(self):
        # __str__ controls what Django shows when it prints this object.
        # e.g. in the admin panel, dropdowns, and debug output.
        return self.username or str(self.user)


# COUNTRY
# Used to support multiple regions with different currencies.
# Both the Product and Order models reference this.
class Country(models.Model):
    name = models.CharField(max_length=100)
    # max_length=5 is enough for codes like "ZA", "US", "UK"
    code = models.CharField(max_length=5)
    # Stores currency codes like "ZAR", "USD", "GBP"
    currency = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# SUPPLIER
# Represents a vendor who supplies products.
# A supplier can fulfill orders via Shopify, manually, or via their own API.
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True)

    # ForeignKey = many-to-one relationship.
    # Many suppliers can be in one country.
    # on_delete=models.CASCADE: if the country is deleted, delete all its suppliers too.
    country = models.ForeignKey(Country,on_delete=models.CASCADE,help_text="Country where the supplier operates")
    active = models.BooleanField(default=True)

    # auto_now_add=True sets this field to the current time ONLY when created.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    # auto_now=True updates this field to the current time EVERY time the record is saved.
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    # choices= restricts the field to a specific list of values.
    # Each tuple is (stored_value, human_readable_label).
    fulfillment_type = models.CharField(max_length=20,
        choices=[
            ('shopify', 'Shopify'),
            ('manual', 'Manual'),
            ('api', 'API'),
        ],
        default='manual',
        help_text="How orders are sent to the supplier"
    )

    def __str__(self):
        return self.name

# CATEGORY
# Groups products together (e.g. "Chargers", "Cables", "Adapters").
class Category(models.Model):
    # unique=True means no two categories can have the same name.
    name = models.CharField(max_length=100, unique=True)

    # slug is a URL-friendly version of the name, e.g. "ev-chargers"
    # Used in URLs like /shop/category/ev-chargers/
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        # Meta class controls model-level settings.
        # verbose_name_plural fixes the Django admin label (default would be "Categorys").
        verbose_name_plural = "Categories"



# CONNECTOR TYPE
# EV-specific — stores charging connector standards like CCS2, Type 2, CHAdeMO.
class ConnectorType(models.Model):
    name = models.CharField(max_length=50)
    region = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ShopifyStore(models.Model):
    # shop_domain stores the full myshopify.com domain, e.g. volt-hub-dev.myshopify.com
    shop_domain = models.CharField(max_length=255, unique=True)
    # The Admin API access token. NEVER expose this in templates or JavaScript.
    access_token = models.CharField(max_length=255, blank=True, null=True)
    # scope stores what permissions were granted during OAuth, e.g. "read_products,write_products"
    scope = models.TextField(blank=True)
    installed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_domain



# PRODUCT
# The central model of your shop. Represents a product synced from Shopify.
class Product(models.Model):
    # ForeignKey to Supplier many products can come from one supplier.
    # on_delete=models.SET_NULL means: if supplier is deleted, keep the product
    # but set supplier to NULL instead of deleting the product too.
    supplier = models.ForeignKey(Supplier,on_delete=models.SET_NULL,null=True,blank=True)
    country = models.ForeignKey(Country,on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=255)

    # TextField is for long text (no max length enforced at DB level).
    # Use it for descriptions, bios, HTML content, etc.
    description = models.TextField()

    # DecimalField is for money — never use FloatField for prices because
    # floats have rounding errors (e.g. 0.1 + 0.2 = 0.30000000000004).
    # max_digits=10 means up to 10 digits total.
    # decimal_places=2 means 2 digits after the decimal point (e.g. 199.99).
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # on_sale and sale_price were commented out in your original but your
    # templates already reference them — adding them back properly.
    on_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)

    # shopify_id links this Django product to its Shopify counterpart.
    # Used by the Admin API sync to match records and avoid duplicates.
    # unique=True means no two products can have the same Shopify ID.
    shopify_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    # shopify_variant_id is CRITICAL for the Storefront API cart.
    # Shopify's cart works with variant IDs, not product IDs.
    # Every product has at least one variant (the default variant).
    # Format: "gid://shopify/ProductVariant/123456789"
    shopify_variant_id = models.CharField(max_length=255, null=True, blank=True)

    # shopify_image_url stores the CDN URL of the product image from Shopify.
    # We store the URL as text instead of downloading the image to our server.
    # This is more efficient — the image stays on Shopify's fast CDN.
    shopify_image_url = models.URLField(null=True, blank=True)

    supplier_price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    supplier_product_url = models.URLField(null=True, blank=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='products')

    # ManyToManyField = many products can have many connector types.
    # Django creates a hidden join table automatically for you.
    compatible_connectors = models.ManyToManyField(ConnectorType, blank=True)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    
    def description_preview(self):
        return format_html(self.description)
        description_preview.short_description = "Description Preview"

    def profit(self):
        # A regular method (not a field) — calculates profit margin on the fly.
        # Returns None if we don't know the supplier price.
        if self.supplier_price:
            return self.price - self.supplier_price
        return None

    @property
    def main_image(self):
        # @property makes this method callable like an attribute: product.main_image
        # Priority: first check for a gallery image marked as primary,
        # then fall back to Shopify's image URL.
        primary = self.gallery.filter(is_primary=True).first()
        if primary:
            return primary.image.url

        # If no primary gallery image, return the Shopify CDN URL
        if self.shopify_image_url:
            return self.shopify_image_url

        # If no image at all, return None — templates should handle this gracefully
        return None

    def __str__(self):
        return self.name



# PRODUCT IMAGE
# Stores additional images for a product (a gallery).
# related_name='gallery' means you can access images via product.gallery.all()
class ProductImage(models.Model):
    # on_delete=models.CASCADE: if the product is deleted, delete all its images too.
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='product_images/gallery')
    alt_text = models.CharField(max_length=150, blank=True)
    is_primary = models.BooleanField(
        default=False,
        help_text="Mark true if this is the primary image for the product"
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"



# ORDER
# Represents a completed purchase. Created when a cart is converted.
class Order(models.Model):
    # STATUS_CHOICES is a class level constant (not a field).
    # It restricts what values can be stored in the 'status' field.
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

    # shopify_order_id links this Django order to the Shopify order.
    # Set by the order/paid webhook when Shopify confirms payment.
    shopify_order_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id}"



# ORDER ITEM
# A single line in an order — one product and its quantity.
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    # We snapshot the price at the time of purchase.
    # This is important because product prices can change later —
    # you don't want old orders to show the wrong price.
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"



# SUPPLIER ORDER
# Tracks which supplier needs to fulfill part of a customer order.
# One customer Order can split across multiple SupplierOrders.
class SupplierOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    shipped = models.BooleanField(default=False)
    tracking_number = models.CharField(max_length=255, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"SupplierOrder #{self.id}"


# ADDRESS
# Stores shipping or billing addresses for users.
# A user can have multiple addresses (OneToMany via ForeignKey).
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"



# CART
# The active shopping basket for a user.
# active=True means this is the user's current open cart.
# active=False means it has been converted to an Order.
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    country = models.ForeignKey('Country', on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)

    # shopify_cart_id stores the cart ID returned by Shopify's Storefront API.
    # Format: "gid://shopify/Cart/abc123..."
    # This is what lets us add items and get a checkoutUrl from Shopify.
    shopify_cart_id = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username} (Active: {self.active})"

    def add_item(self, product, quantity=1):
        # get_or_create either fetches an existing CartItem or creates a new one.
        # It returns a tuple: (object, created_boolean)
        item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={'price_at_time': product.price}
        )
        if not created:
            # Item already in cart — just increase the quantity
            item.quantity += quantity
        else:
            item.quantity = quantity

        # Always refresh the price snapshot in case the price changed
        item.price_at_time = product.price
        item.save()

    def remove_item(self, product):
        CartItem.objects.filter(cart=self, product=product).delete()

    def clear_items(self):
        # self.items.all() uses the related_name='items' we set on CartItem
        self.items.all().delete()

    def total_price(self):
        # sum() with a generator expression — pythonic way to total a list
        return sum(item.subtotal() for item in self.items.all())

    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    def convert_to_order(self, shipping_address):
        if not self.active:
            raise ValueError("Cannot convert an inactive cart to order.")

        order = Order.objects.create(
            user=self.user,
            country=self.country,
            total_amount=self.total_price(),
            shipping_address=shipping_address
        )

        for item in self.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.price_at_time
            )
            # get_or_create prevents duplicate SupplierOrders for the same supplier
            SupplierOrder.objects.get_or_create(
                supplier=item.product.supplier,
                order=order
            )

        # Mark cart as inactive so it can't be used again
        self.active = False
        self.save()

        return order


# CART ITEM
# A single product inside a cart with its quantity and price snapshot.
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    # Price at the time the item was added — protects against price changes
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def subtotal(self):
        # price_at_time × quantity = line total for this cart item
        return self.price_at_time * self.quantity

    def supplier(self):
        # Convenience accessor — get the supplier through the product
        return self.product.supplier

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"

    class Meta:
        # unique_together prevents the same product appearing twice in one cart.
        # Instead of two rows for the same product, quantity is incremented.
        unique_together = ('cart', 'product')
        ordering = ['created_at']


# WISHLIST
# A user's saved products for later.
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist of {self.user.username}"

    def total_items(self):
        return self.products.count()

    def add_item(self, product):
        # get_or_create is safe to call multiple times — won't add duplicates
        WishlistItem.objects.get_or_create(wishlist=self, product=product)

    def remove_item(self, product):
        WishlistItem.objects.filter(wishlist=self, product=product).delete()

    def clear_items(self):
        self.items.all().delete()


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.user.username}'s wishlist"


# REVIEW
# User reviews and ratings for products.
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')

    # validators enforce min/max values at the Django level (before hitting the DB)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

    class Meta:
        # Prevents a user from reviewing the same product more than once
        unique_together = ('product', 'user')