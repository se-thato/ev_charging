# This file handles ALL communication with Shopify's Storefront API.
# The Storefront API is PUBLIC — it uses a token that is safe to use
# server-side. It handles the cart and checkout flow.
#
# KEY DIFFERENCE from Admin API:
#   Admin API  → server only, private token, manages your store data
#   Storefront → powers the shopping experience, cart, and checkout
#
# HOW THE CART FLOW WORKS:
#   1. User clicks "Add to Cart" → we call Shopify to create/update a cart
#   2. Shopify gives us back a cart ID and a checkoutUrl
#   3. We store the cart ID in the Django session (like a temporary note)
#   4. When user clicks "Checkout" → we redirect them to Shopify's checkoutUrl
#   5. Shopify handles payment, shipping, confirmation — everything

import requests
from django.conf import settings

# The Storefront API uses GraphQL — a query language where you describe
# exactly what data you want, and Shopify returns exactly that.
# REST API: GET /products → returns ALL product fields whether you need them or not
# GraphQL:  you ask for only name + price → you only get name + price

STOREFRONT_URL = f"https://{settings.SHOPIFY_SHOP_DOMAIN}/api/2024-01/graphql.json"


def _storefront_request(query, variables=None):
    """
    Internal helper — sends a GraphQL request to Shopify's Storefront API.
    All the functions below call this one function, keeping things DRY
    (Don't Repeat Yourself).

    Parameters:
        query     : a GraphQL query string (what data you want / what action to do)
        variables : a Python dict of values to inject into the query

    Returns:
        The 'data' section of Shopify's response as a Python dict,
        or None if the request failed.
    """

    headers = {
        # This is the PUBLIC Storefront access token.
        # Safe to use server-side. Never use your Admin API token here.
        "X-Shopify-Storefront-Access-Token": settings.SHOPIFY_STOREFRONT_TOKEN,
        "Content-Type": "application/json",
    }

    # GraphQL requests are always POST, even when just reading data.
    # We send the query and variables as a JSON body.
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    try:
        response = requests.post(
            STOREFRONT_URL,
            json=payload,
            headers=headers,
            timeout=10  # don't wait more than 10 seconds
        )

        if response.status_code != 200:
            print(f"[Storefront] HTTP {response.status_code}: {response.text}")
            return None

        result = response.json()

        # GraphQL can return HTTP 200 but still have logical errors in the body.
        # Always check for the 'errors' key separately.
        if "errors" in result:
            print(f"[Storefront] GraphQL errors: {result['errors']}")
            return None

        # Return only the 'data' section — that's where the actual results are
        return result.get("data")

    except requests.exceptions.RequestException as e:
        # This catches network errors, timeouts, DNS failures, etc.
        print(f"[Storefront] Request failed: {e}")
        return None


def create_cart(variant_id, quantity=1):
    """
    Creates a brand new cart in Shopify with one item already in it.

    Parameters:
        variant_id : the Shopify variant GID, e.g. "gid://shopify/ProductVariant/123"
        quantity   : how many of this item to add (default 1)

    Returns:
        A dict with 'cart_id' and 'checkout_url', or None on failure.

    WHY THIS MATTERS:
        Shopify's cart lives on THEIR servers, not in our database.
        We just store the cart ID in the Django session so we can
        reference it again when the user adds more items.
    """

    # This is a GraphQL mutation — mutations CHANGE data (like a POST/PUT in REST).
    # Queries only READ data. Mutations create, update, or delete.
    #
    # $lines is a variable — the $ prefix means it's injected from 'variables' below.
    # [CartLineInput!]! means: a non-empty list of CartLineInput objects, required.
    mutation = """
    mutation CreateCart($lines: [CartLineInput!]!) {
      cartCreate(input: { lines: $lines }) {
        cart {
          id
          checkoutUrl
          totalQuantity
          cost {
            totalAmount {
              amount
              currencyCode
            }
          }
          lines(first: 10) {
            edges {
              node {
                id
                quantity
                merchandise {
                  ... on ProductVariant {
                    id
                    title
                    price {
                      amount
                    }
                    product {
                      title
                    }
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
    """

    # Variables are injected into the mutation above wherever $lines appears.
    # merchandiseId is Shopify's term for the variant GID.
    variables = {
        "lines": [
            {
                "merchandiseId": variant_id,
                "quantity": quantity
            }
        ]
    }

    data = _storefront_request(mutation, variables)
    if not data:
        return None

    # Navigate the nested response: data → cartCreate → cart
    cart_data = data.get("cartCreate", {})

    # userErrors are Shopify-level validation errors (different from GraphQL errors).
    # Example: trying to add more items than are in stock.
    user_errors = cart_data.get("userErrors", [])
    if user_errors:
        print(f"[Storefront] Cart create errors: {user_errors}")
        return None

    cart = cart_data.get("cart")
    if not cart:
        return None

    return {
        "cart_id": cart["id"],            # e.g. "gid://shopify/Cart/abc123..."
        "checkout_url": cart["checkoutUrl"],  # e.g. "https://volt-hub-dev.myshopify.com/cart/c/abc123"
        "total_quantity": cart["totalQuantity"],
        "total_amount": cart["cost"]["totalAmount"]["amount"],
        "currency": cart["cost"]["totalAmount"]["currencyCode"],
        "lines": _parse_cart_lines(cart.get("lines", {}).get("edges", [])),
    }


def add_to_cart(cart_id, variant_id, quantity=1):
    """
    Adds an item to an EXISTING Shopify cart.
    Called when user is already shopping and adds another product.

    Parameters:
        cart_id    : the Shopify cart GID we stored in the session
        variant_id : the product variant GID to add
        quantity   : how many to add

    Returns:
        Updated cart dict or None on failure.
    """

    mutation = """
    mutation AddToCart($cartId: ID!, $lines: [CartLineInput!]!) {
      cartLinesAdd(cartId: $cartId, lines: $lines) {
        cart {
          id
          checkoutUrl
          totalQuantity
          cost {
            totalAmount {
              amount
              currencyCode
            }
          }
          lines(first: 20) {
            edges {
              node {
                id
                quantity
                merchandise {
                  ... on ProductVariant {
                    id
                    title
                    price {
                      amount
                    }
                    product {
                      title
                    }
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
    """

    variables = {
        "cartId": cart_id,
        "lines": [{"merchandiseId": variant_id, "quantity": quantity}]
    }

    data = _storefront_request(mutation, variables)
    if not data:
        return None

    cart_data = data.get("cartLinesAdd", {})
    user_errors = cart_data.get("userErrors", [])
    if user_errors:
        print(f"[Storefront] Add to cart errors: {user_errors}")
        return None

    cart = cart_data.get("cart")
    if not cart:
        return None

    return {
        "cart_id": cart["id"],
        "checkout_url": cart["checkoutUrl"],
        "total_quantity": cart["totalQuantity"],
        "total_amount": cart["cost"]["totalAmount"]["amount"],
        "currency": cart["cost"]["totalAmount"]["currencyCode"],
        "lines": _parse_cart_lines(cart.get("lines", {}).get("edges", [])),
    }


def remove_from_cart(cart_id, line_id):
    """
    Removes a specific line from a Shopify cart.
    Note: line_id is the CART LINE id (not the variant id).
    Each item in the cart has its own line ID.
    """

    mutation = """
    mutation RemoveFromCart($cartId: ID!, $lineIds: [ID!]!) {
      cartLinesRemove(cartId: $cartId, lineIds: $lineIds) {
        cart {
          id
          checkoutUrl
          totalQuantity
          cost {
            totalAmount {
              amount
              currencyCode
            }
          }
          lines(first: 20) {
            edges {
              node {
                id
                quantity
                merchandise {
                  ... on ProductVariant {
                    id
                    title
                    price { amount }
                    product { title }
                  }
                }
              }
            }
          }
        }
        userErrors { field message }
      }
    }
    """

    variables = {"cartId": cart_id, "lineIds": [line_id]}
    data = _storefront_request(mutation, variables)
    if not data:
        return None

    cart_data = data.get("cartLinesRemove", {})
    cart = cart_data.get("cart")
    if not cart:
        return None

    return {
        "cart_id": cart["id"],
        "checkout_url": cart["checkoutUrl"],
        "total_quantity": cart["totalQuantity"],
        "total_amount": cart["cost"]["totalAmount"]["amount"],
        "currency": cart["cost"]["totalAmount"]["currencyCode"],
        "lines": _parse_cart_lines(cart.get("lines", {}).get("edges", [])),
    }


def get_cart(cart_id):
    """
    Fetches the current state of a cart from Shopify.
    Used to display the cart page with up-to-date prices and quantities.
    """

    # This is a GraphQL QUERY (not a mutation) — it only reads data.
    query = """
    query GetCart($cartId: ID!) {
      cart(id: $cartId) {
        id
        checkoutUrl
        totalQuantity
        cost {
          totalAmount {
            amount
            currencyCode
          }
        }
        lines(first: 20) {
          edges {
            node {
              id
              quantity
              merchandise {
                ... on ProductVariant {
                  id
                  title
                  price { amount }
                  product { title featuredImage { url } }
                }
              }
            }
          }
        }
      }
    }
    """

    data = _storefront_request(query, {"cartId": cart_id})
    if not data:
        return None

    cart = data.get("cart")
    if not cart:
        return None

    return {
        "cart_id": cart["id"],
        "checkout_url": cart["checkoutUrl"],
        "total_quantity": cart["totalQuantity"],
        "total_amount": cart["cost"]["totalAmount"]["amount"],
        "currency": cart["cost"]["totalAmount"]["currencyCode"],
        "lines": _parse_cart_lines(cart.get("lines", {}).get("edges", [])),
    }


def _parse_cart_lines(edges):
    """
    Helper to convert Shopify's nested GraphQL cart lines into a clean
    flat list that's easy to loop over in Django templates.

    GraphQL returns data in nested 'edges' → 'node' structure.
    This is because GraphQL supports pagination — edges can have cursor info.
    We flatten it for convenience.
    """
    lines = []
    for edge in edges:
        node = edge.get("node", {})
        merchandise = node.get("merchandise", {})
        product = merchandise.get("product", {})
        image = product.get("featuredImage")

        lines.append({
            "line_id": node.get("id"),           # needed to remove this line
            "quantity": node.get("quantity"),
            "variant_id": merchandise.get("id"),
            "variant_title": merchandise.get("title"),
            "price": merchandise.get("price", {}).get("amount"),
            "product_title": product.get("title"),
            "image_url": image.get("url") if image else None,
        })
    return lines