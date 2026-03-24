from django.contrib import admin
from .models import (
    Product, ProductImage, Category, Supplier,
    Country, ConnectorType, ShopifyStore,
    Order, OrderItem, SupplierOrder,
    Cart, CartItem,
    Wishlist, WishlistItem,
    Review, Address, Profile
)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('price_at_time', 'created_at')
    fields = ('product', 'quantity', 'price_at_time', 'created_at')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary')
    max_num = 10


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'active', 'total_items', 'total_price', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]

    def total_items(self, obj):
        return obj.items.count()
    total_items.short_description = 'Items'

    def total_price(self, obj):
        return f"R{obj.total_price()}"
    total_price.short_description = 'Total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart_user', 'product', 'quantity', 'price_at_time', 'subtotal', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('cart__user__username', 'product__name')
    readonly_fields = ('price_at_time', 'created_at')

    def cart_user(self, obj):
        return obj.cart.user.username
    cart_user.short_description = 'User'

    def subtotal(self, obj):
        return f"R{obj.subtotal()}"
    subtotal.short_description = 'Subtotal'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'on_sale', 'sale_price', 'active', 'shopify_id')
    list_filter = ('active', 'on_sale', 'category')
    search_fields = ('name', 'shopify_id', 'description')
    readonly_fields = ('created_at', 'shopify_id', 'shopify_variant_id', 'shopify_image_url')
    inlines = [ProductImageInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'category', 'supplier', 'country', 'active')
        }),
        ('Pricing', {
            'fields': ('price', 'on_sale', 'sale_price', 'supplier_price')
        }),
        ('Shopify Sync', {
            'fields': ('shopify_id', 'shopify_variant_id', 'shopify_image_url'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'payment_reference', 'shopify_order_id')
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'country', 'fulfillment_type', 'active')
    list_filter = ('active', 'fulfillment_type', 'country')
    search_fields = ('name', 'email')


@admin.register(ShopifyStore)
class ShopifyStoreAdmin(admin.ModelAdmin):
    list_display = ('shop_domain', 'scope', 'installed_at')
    readonly_fields = ('installed_at',)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'currency', 'is_active')
    list_filter = ('is_active',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('product__name', 'user__username')


# Simple registrations — no custom admin needed
admin.site.register(ConnectorType)
admin.site.register(SupplierOrder)
admin.site.register(Wishlist)
admin.site.register(WishlistItem)
admin.site.register(Address)
admin.site.register(Profile)