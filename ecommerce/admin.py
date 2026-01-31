from django.contrib import admin
from .models import Product, Category, ProductImage, Order, OrderItem, CartItem, Cart, Customer, Review, Wishlist, WishlistItem, Address, Profile,Country, Supplier,ConnectorType,SupplierOrder


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Show one blank image field by default
    max_num = 10  # Maximum images per product

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name', 'price', 'supplier', 'active')
    list_filter = ('category', 'active', 'supplier')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    

admin.site.register(Product, ProductAdmin)

admin.site.register(Category)

admin.site.register(Address)

admin.site.register(Review)

admin.site.register(Cart)

admin.site.register(CartItem)

admin.site.register(Order)

admin.site.register(OrderItem)

admin.site.register(Customer)

admin.site.register(Wishlist)

admin.site.register(WishlistItem)

admin.site.register(Profile)

admin.site.register(Country)

admin.site.register(Supplier)

admin.site.register(ConnectorType)

admin.site.register(SupplierOrder)

