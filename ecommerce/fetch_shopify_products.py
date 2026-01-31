import shopify
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ev_charging.settings")
django.setup()

from ecommerce.models import Product, Supplier, Category

# Shopify credentials
SHOP_URL = "https://{API_KEY}:{ACCESS_TOKEN}@volt-hub-dev.myshopify.com/admin/api/2026-01"
shopify.ShopifyResource.set_site(SHOP_URL)

def get_or_create_supplier(shopify_product):
    supplier_name = shopify_product.vendor or "Unknown Supplier"
    supplier, created = Supplier.objects.get_or_create(
        name=supplier_name,
        defaults={
            "website": shopify_product.vendor,  # You may change if actual website exists
            "email": "",  # Optional, leave blank if missing
            "whatsapp": "",
            "country": None
        }
    )
    return supplier

def get_or_create_category(shopify_product):
    category_name = shopify_product.product_type or "Uncategorized"
    category, _ = Category.objects.get_or_create(name=category_name)
    return category

def fetch_shopify_products():
    products = shopify.Product.find()
    for sp in products:
        supplier = get_or_create_supplier(sp)
        category = get_or_create_category(sp)

        # Some Shopify products may have multiple variants
        price = float(sp.variants[0].price) if sp.variants else 0

        # Take first image if exists
        image_url = sp.images[0].src if sp.images else None

        product, created = Product.objects.get_or_create(
            name=sp.title,
            defaults={
                "supplier": supplier,
                "category": category,
                "price": price,
                "supplier_price": None,
                "supplier_product_url": f"https://{sp.handle}.myshopify.com",
                "description": sp.body_html or "",
                "active": True,
                "image": image_url
            }
        )
        if not created:
            # This will update price or description if product already exists
            product.price = price
            product.description = sp.body_html or ""
            product.save()

    print("Shopify products synced successfully!")

if __name__ == "__main__":
    fetch_shopify_products()
