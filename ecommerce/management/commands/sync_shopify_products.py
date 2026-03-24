# management/commands/sync_shopify_products.py
# ─────────────────────────────────────────────────────────────────────────────
# Django management commands are custom commands you run from the terminal.
# This one syncs all products from your Shopify store into your Django database.
#
# HOW TO RUN:
#   python manage.py sync_shopify_products
#
# FOLDER STRUCTURE REQUIRED:
#   ecommerce/
#     management/
#       __init__.py          ← empty file, tells Python this is a package
#       commands/
#         __init__.py        ← empty file, tells Python this is a package
#         sync_shopify_products.py   ← this file
#
# WHY A MANAGEMENT COMMAND instead of a regular view?
#   - It runs on the server without a browser request
#   - You can schedule it with a cron job (e.g. sync every night at midnight)
#   - It's safe — no user can accidentally trigger it from the web
# ─────────────────────────────────────────────────────────────────────────────

import requests                          # for making HTTP requests to Shopify
from django.core.management.base import BaseCommand  # base class for all management commands
from django.conf import settings         # access to settings.py variables
from ecommerce.models import Country, Product, Supplier, Category, ShopifyStore


class Command(BaseCommand):
    # help text is shown when you run: python manage.py sync_shopify_products --help
    help = 'Syncs all products from your Shopify store into the Django database'

    def handle(self, *args, **kwargs):
        # handle() is the method Django calls when you run this command.
        # *args and **kwargs let Django pass extra command-line arguments.

        # ── Step 1: Get the stored Shopify credentials from the database ──────
        # We fetch the ShopifyStore record that was saved during OAuth.
        # .first() returns the first result or None if the table is empty.
        store = ShopifyStore.objects.first()

        if not store:
            # self.stderr.write prints in RED — used for errors
            self.stderr.write("No Shopify store connected. Run OAuth first at /shopify/auth/")
            return  # stop execution here

        # ── Step 2: Call the Shopify Admin REST API ───────────────────────────
        # The Admin REST API endpoint for products:
        # GET https://{shop_domain}/admin/api/2024-01/products.json
        # ?limit=250 fetches up to 250 products per page (Shopify's maximum)
        url = f"https://{store.shop_domain}/admin/api/2024-01/products.json?limit=250"

        # The X-Shopify-Access-Token header authenticates the request.
        # This is your PRIVATE admin token — never put this in JavaScript or templates.
        headers = {
            "X-Shopify-Access-Token": store.access_token,
            "Content-Type": "application/json"
        }

        # requests.get() sends an HTTP GET request and waits for the response.
        # timeout=15 means stop waiting after 15 seconds (prevents hanging forever).
        response = requests.get(url, headers=headers, timeout=15)

        # status_code 200 means success. Any other code means something went wrong.
        if response.status_code != 200:
            self.stderr.write(f"Shopify API error {response.status_code}: {response.text}")
            return

        # .json() converts the response body from a JSON string into a Python dict
        data = response.json()

        # Shopify wraps the products list in a "products" key
        shopify_products = data.get("products", [])

        # self.stdout.write prints in GREEN — used for progress/success messages
        self.stdout.write(f"Found {len(shopify_products)} products in Shopify. Syncing...")

        # ── Step 3: Loop through each Shopify product and save to Django DB ───
        synced = 0   # counter for how many were synced
        errors = 0   # counter for how many failed

        for sp in shopify_products:
            try:
                # ── 3a. Get or create the Category ───────────────────────────
                # sp.get("product_type") reads the 'product_type' key from the
                # Shopify product JSON. If it's empty, we use "Uncategorized".
                category_name = sp.get("product_type") or "Uncategorized"

                # get_or_create looks for a Category with this name.
                # If it doesn't exist, it creates one.
                # The _ means we don't need the 'created' boolean it returns.
                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    defaults={
                        # defaults= only used when CREATING, not when fetching
                        'slug': category_name.lower().replace(' ', '-')
                    }
                )

                # ── 3b. Get or create the Supplier ───────────────────────────
                # Shopify stores the brand/vendor name in the 'vendor' field.
                supplier_name = sp.get("vendor") or "Unknown Supplier"
                supplier, _ = Supplier.objects.get_or_create(
                    name=supplier_name,
                    defaults={
                        # We need a country for the supplier FK.
                        # get_or_create a default country to avoid errors.
                        'country': self._get_default_country(),
                        'fulfillment_type': 'shopify',
                    }
                )

                # ── 3c. Get variant data ──────────────────────────────────────
                # Shopify products have "variants" — each variant is a
                # specific version of the product (e.g. different size/colour).
                # For simplicity we use the FIRST variant for price and ID.
                variants = sp.get("variants", [])
                first_variant = variants[0] if variants else {}

                # Shopify stores prices as strings like "199.99" — convert to float
                price = float(first_variant.get("price", 0))

                # compare_at_price is the original (crossed-out) price for sale items
                compare_at = first_variant.get("compare_at_price")
                on_sale = compare_at is not None and float(compare_at) > price
                sale_price = price if on_sale else None
                original_price = float(compare_at) if on_sale else price

                # variant_id in Shopify GraphQL format: "gid://shopify/ProductVariant/123"
                # The Storefront API needs this exact format to add items to a cart.
                raw_variant_id = first_variant.get("id")  # this is a plain integer from REST
                shopify_variant_gid = f"gid://shopify/ProductVariant/{raw_variant_id}"

                # ── 3d. Get image URL ─────────────────────────────────────────
                images = sp.get("images", [])
                image_url = images[0].get("src") if images else None

                # ── 3e. Build the shopify_id in GID format ────────────────────
                # We store it as the GraphQL Global ID for consistency
                shopify_gid = f"gid://shopify/Product/{sp.get('id')}"

                # ── 3f. Save to Django database ───────────────────────────────
                # update_or_create:
                #   - Looks for a Product WHERE shopify_id = shopify_gid
                #   - If found: UPDATES it with the values in 'defaults'
                #   - If not found: CREATES a new Product with shopify_id + defaults
                # This is safer than get_or_create because it keeps data fresh.
                product, created = Product.objects.update_or_create(
                    shopify_id=shopify_gid,
                    defaults={
                        "name": sp.get("title", ""),
                        "description": sp.get("body_html") or "",
                        "price": original_price,
                        "on_sale": on_sale,
                        "sale_price": sale_price,
                        "shopify_variant_id": shopify_variant_gid,
                        "shopify_image_url": image_url,
                        "supplier": supplier,
                        "category": category,
                        "active": (sp.get("status") == "active"),
                        # status "active" in Shopify = visible in store
                    }
                )

                synced += 1
                action = "Created" if created else "Updated"
                self.stdout.write(f"  {action}: {product.name}")

            except Exception as e:
                # Catch any error for THIS product and continue with the next one.
                # Without this try/except, one bad product would crash the whole sync.
                errors += 1
                self.stderr.write(f"  ERROR syncing '{sp.get('title')}': {e}")

        # ── Step 4: Print summary ─────────────────────────────────────────────
        # self.style.SUCCESS wraps text in green colour
        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Synced: {synced} products. Errors: {errors}"
        ))

    def _get_default_country(self):
        # Helper method — gets or creates a default country for new suppliers.
        # The underscore prefix is a Python convention meaning "internal/private method".
        # We use South Africa as the default since your store is in ZA.
        country, _ = Country.objects.get_or_create(
            code="ZA",
            defaults={"name": "South Africa", "currency": "ZAR"}
        )
        return country


# ─────────────────────────────────────────────────────────────────────────────
# WHAT TO DO AFTER RUNNING THIS:
#
# 1. The first time: python manage.py sync_shopify_products
#    → This populates your Product table from Shopify
#
# 2. For automatic syncing, add this to your server's cron (Linux scheduler):
#    0 3 * * * /path/to/venv/bin/python /path/to/manage.py sync_shopify_products
#    → Runs every night at 3am
#
# 3. For REAL-TIME syncing (product changes appear instantly),
#    use webhooks — see webhooks.py
# ─────────────────────────────────────────────────────────────────────────────