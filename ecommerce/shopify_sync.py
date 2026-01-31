import requests
from django.conf import settings
from .models import Product, Supplier, Category, Country

def fetch_shopify_products():
    """
    Fetch all products from Shopify and sync them to local Product model.
    """

    # Shopify REST Admin API endpoint
    url = f"https://{settings.SHOPIFY_SHOP_NAME}/admin/api/2026-01/products.json"

    # Headers include the access token for authentication
    headers = {
        "X-Shopify-Access-Token": settings.SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Error fetching products:", response.text)
        return

    data = response.json()
    shopify_products = data.get("products", [])

    for sp in shopify_products:
        # Handle supplier info (we can create a default supplier if not provided)
        supplier, _ = Supplier.objects.get_or_create(name="Shopify Supplier")

        # Handle category (if Shopify product has a type, use it; else default)
        category_name = sp.get("product_type") or "Uncategorized"
        category, _ = Category.objects.get_or_create(name=category_name)

        # Save product to local DB
        product, created = Product.objects.update_or_create(
            name=sp.get("title"),
            defaults={
                "description": sp.get("body_html") or "",
                "price": sp.get("variants")[0].get("price") if sp.get("variants") else 0,
                "supplier_price": None,
                "supplier_product_url": sp.get("admin_graphql_api_id"),
                "supplier": supplier,
                "category": category,
                "active": True,
            }
        )

        # Handle images (take first image for main image)
        images = sp.get("images", [])
        if images:
            product.image = images[0].get("src")
            product.save()

    print(f"Synced {len(shopify_products)} products from Shopify.")
