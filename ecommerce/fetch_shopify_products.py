import shopify
import os
import django



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ev_charging.settings")
django.setup()

from ecommerce.models import Product, Supplier, Category

from django.utils.html import strip_tags
import bleach

# Allow only safe tags, strip everything else
ALLOWED_TAGS = ['p', 'b', 'i', 'ul', 'ol', 'li', 'br', 'span', 'h1', 'h2', 'h3', 'img']
ALLOWED_ATTRS = {'img': ['src', 'alt'], 'span': ['style'], '*': []}

clean_description = bleach.clean(raw_description, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)



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
    all_products = []
    page = shopify.Product.find(limit=250, status='active')
    all_products.extend(page)
    
    while page.has_next_page():
        page = page.next_page()
        all_products.extend(page)
    
    print(f"Found {len(all_products)} products in Shopify. Syncing...")
    
    synced = 0
    errors = 0
    for sp in all_products:
        try:
            supplier = get_or_create_supplier(sp)
            category = get_or_create_category(sp)
            price = float(sp.variants[0].price) if sp.variants else 0
            image_url = sp.images[0].src if sp.images else None
            variant_id = str(sp.variants[0].id) if sp.variants else None

            product, created = Product.objects.update_or_create(
                shopify_id=str(sp.id),
                defaults={
                    "name": sp.title,
                    "supplier": supplier,
                    "category": category,
                    "price": price,
                    "supplier_price": None,
                    "supplier_product_url": f"https://volt-hub-dev.myshopify.com/products/{sp.handle}",
                    "description": sp.body_html or "",
                    "active": (sp.status == "active"),
                    "shopify_image_url": image_url,
                    "shopify_variant_id": variant_id,
                }
            )
            action = "Created" if created else "Updated"
            print(f"  {action}: {sp.title[:60]}")
            synced += 1
        except Exception as e:
            print(f"  ERROR on {sp.title[:60]}: {e}")
            errors += 1

    print(f"Done! Synced: {synced} products. Errors: {errors}")


# def fetch_shopify_products():
#     products = shopify.Product.find()
#     for sp in products:
#         supplier = get_or_create_supplier(sp)
#         category = get_or_create_category(sp)

#         # Some Shopify products may have multiple variants
#         price = float(sp.variants[0].price) if sp.variants else 0

#         # Take first image if exists
#         image_url = sp.images[0].src if sp.images else None

#         product, created = Product.objects.get_or_create(
#             name=sp.title,
#             defaults={
#                 "supplier": supplier,
#                 "category": category,
#                 "price": price,
#                 "supplier_price": None,
#                 "supplier_product_url": f"https://{sp.handle}.myshopify.com",
#                 "description": sp.body_html or "",
#                 "active": True,
#                 "image": image_url
#             }
#         )
#         if not created:
#             # This will update price or description if product already exists
#             product.price = price
#             product.description = sp.body_html or ""
#             product.save()

#     print("Shopify products synced successfully!")

# if __name__ == "__main__":
#     fetch_shopify_products()
