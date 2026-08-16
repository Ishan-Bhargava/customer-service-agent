"""
Mock dataset for a customer-service returns agent.

Three linked dictionaries, keyed by ID, mimicking what a real backend
would expose:
    CUSTOMERS  -- who's asking (now includes a password_hash for login)
    PRODUCTS   -- what they bought (with return policy per product)
    ORDERS     -- the actual purchase record linking customer + product,
                  with enough detail (order date, delivery date, status)
                  to decide whether a return is even valid

A few small helper/lookup functions are included at the bottom -- these
are the kind of thing you'd later wrap as @tool functions for the agent
(e.g. get_order_by_id, is_within_return_window), but they're plain
functions here so you can test the data itself first, before any agent
is involved.

AUTH NOTE:
    Every customer now has a `password_hash` field (werkzeug
    pbkdf2:sha256 hashes -- never store plaintext passwords, even in a
    demo). Plaintext test passwords are listed in TEST_LOGINS at the
    bottom of this file so you can actually log in during development.
    Use `verify_password(customer, plaintext)` to check a login attempt.

Run this file directly to print a quick sanity-check of the data.
"""
from datetime import date, timedelta

from werkzeug.security import check_password_hash

# ---------------------------------------------------------------------------
# CUSTOMERS
# ---------------------------------------------------------------------------
CUSTOMERS = {
    "CUST-1001": {
        "customer_id": "CUST-1001",
        "username": "priya.sharma",
        "full_name": "Priya Sharma",
        "email": "priya.sharma@example.com",
        "phone": "+91-98765-43210",
        "member_since": "2023-03-14",
        "loyalty_tier": "gold",
        "password_hash": "pbkdf2:sha256:1000000$SeQYO7UfZTQcH3FE$d7b6f65621450c4f46f79bb04a7fbec6b14aaf30305da09a8cf90db97509e392",
    },
    "CUST-1002": {
        "customer_id": "CUST-1002",
        "username": "arjun.mehta",
        "full_name": "Arjun Mehta",
        "email": "arjun.mehta@example.com",
        "phone": "+91-98123-45678",
        "member_since": "2024-07-01",
        "loyalty_tier": "silver",
        "password_hash": "pbkdf2:sha256:1000000$KOwDKOQUrvejnwtk$874104f288531e0a1c5c8aab007eb8de857131da16114d6a496de4a9c78ccf27",
    },
    "CUST-1003": {
        "customer_id": "CUST-1003",
        "username": "sneha.k",
        "full_name": "Sneha Kulkarni",
        "email": "sneha.k@example.com",
        "phone": "+91-99887-76655",
        "member_since": "2022-11-20",
        "loyalty_tier": "platinum",
        "password_hash": "pbkdf2:sha256:1000000$y81GrjKk1I74ORki$52b8b64f27c4e10d3627cdf57df4b4ab22b7e2923b9f86d2b12b3f43b9b919a1",
    },
    "CUST-1004": {
        "customer_id": "CUST-1004",
        "username": "rohan.d",
        "full_name": "Rohan Deshmukh",
        "email": "rohan.d@example.com",
        "phone": "+91-90000-11223",
        "member_since": "2025-01-09",
        "loyalty_tier": "silver",
        "password_hash": "pbkdf2:sha256:1000000$ZOxojXkfxAFqzMuP$5b77fdcc60cc1ee5c98a90106d8a2f848eedf159968dfd42b359406f0f724cb8",
    },
    "CUST-1005": {
        "customer_id": "CUST-1005",
        "username": "fatima.ansari",
        "full_name": "Fatima Ansari",
        "email": "fatima.ansari@example.com",
        "phone": "+91-97654-32109",
        "member_since": "2021-05-30",
        "loyalty_tier": "platinum",
        "password_hash": "pbkdf2:sha256:1000000$a0ScnLWeeF6I2fez$6c75ce6e01c63f5a68e64d0615ee266a08ebbacce313cf761519150c1c43403f",
    },
    # NOTE: this key used to be "   " (three spaces) in the original data,
    # which meant get_customer("CUST-1006") could never find Vikram Rao
    # even though his own customer_id field said CUST-1006. Fixed here so
    # login by customer_id actually works.
    "CUST-1006": {
        "customer_id": "CUST-1006",
        "username": "vikram.rao",
        "full_name": "Vikram Rao",
        "email": "vikram.rao@example.com",
        "phone": "+91-96543-21098",
        "member_since": "2025-09-12",
        "loyalty_tier": "bronze",
        "password_hash": "pbkdf2:sha256:1000000$kXJGECFgB9cvXxQs$e79c1f8c4e7108fbb6a48300a241f15f8b8ec9f9971e0308520643f7e28456f2",
    },
    "CUST-1007": {
        "customer_id": "CUST-1007",
        "username": "ananya.iyer",
        "full_name": "Ananya Iyer",
        "email": "ananya.iyer@example.com",
        "phone": "+91-95432-10987",
        "member_since": "2026-02-18",
        "loyalty_tier": "bronze",
        "password_hash": "pbkdf2:sha256:1000000$huAMXrRixbtxokDU$21748cd7d52e1f47c895171edb7a517c693ad18f54f8105d275e6380d1ed7239",
    },
    # No orders at all -- useful for testing "empty history" paths
    "CUST-1008": {
        "customer_id": "CUST-1008",
        "username": "karan.bose",
        "full_name": "Karan Bose",
        "email": "karan.bose@example.com",
        "phone": "+91-94321-09876",
        "member_since": "2026-06-01",
        "loyalty_tier": "bronze",
        "password_hash": "pbkdf2:sha256:1000000$RkZEMAII6UfKIRD0$b8c15c4ca1b766a757a82e381ea94c70ff1d678aa697dd63a9661c3ff8ceac87",
    },
}

# Plaintext test passwords -- for local dev/login testing only. In a real
# system these would never be written down anywhere.
TEST_LOGINS = {
    "priya.sharma": "priya123",
    "arjun.mehta": "arjun456",
    "sneha.k": "sneha789",
    "rohan.d": "rohan321",
    "fatima.ansari": "fatima654",
    "vikram.rao": "vikram987",
    "ananya.iyer": "ananya159",
    "karan.bose": "karan753",
}

# ---------------------------------------------------------------------------
# PRODUCTS
# ---------------------------------------------------------------------------
# return_window_days: how many days after DELIVERY a return is allowed
# returnable: some categories (e.g. innerwear, perishables) are policy-excluded
PRODUCTS = {
    "PROD-2001": {
        "product_id": "PROD-2001",
        "name": "Wireless Bluetooth Headphones",
        "category": "electronics",
        "price": 2499.00,
        "return_window_days": 10,
        "returnable": True,
    },
    "PROD-2002": {
        "product_id": "PROD-2002",
        "name": "Running Shoes - Size 9",
        "category": "footwear",
        "price": 3299.00,
        "return_window_days": 30,
        "returnable": True,
    },
    "PROD-2003": {
        "product_id": "PROD-2003",
        "name": "Stainless Steel Water Bottle",
        "category": "home_kitchen",
        "price": 799.00,
        "return_window_days": 15,
        "returnable": True,
    },
    "PROD-2004": {
        "product_id": "PROD-2004",
        "name": "Men's Cotton Innerwear (Pack of 3)",
        "category": "apparel_innerwear",
        "price": 599.00,
        "return_window_days": 0,
        "returnable": False,  # hygiene policy exclusion
    },
    "PROD-2005": {
        "product_id": "PROD-2005",
        "name": "4K Smart TV - 43 inch",
        "category": "electronics",
        "price": 28999.00,
        "return_window_days": 7,
        "returnable": True,
    },
    "PROD-2006": {
        "product_id": "PROD-2006",
        "name": "Ceramic Dinner Set (12 pcs)",
        "category": "home_kitchen",
        "price": 1899.00,
        "return_window_days": 15,
        "returnable": True,
    },
    "PROD-2007": {
        "product_id": "PROD-2007",
        "name": "Organic Assam Tea (250g)",
        "category": "grocery_perishable",
        "price": 349.00,
        "return_window_days": 0,
        "returnable": False,  # perishable, policy-excluded
    },
    "PROD-2008": {
        "product_id": "PROD-2008",
        "name": "Yoga Mat - Extra Thick",
        "category": "sports_fitness",
        "price": 1199.00,
        "return_window_days": 20,
        "returnable": True,
    },
    "PROD-2009": {
        "product_id": "PROD-2009",
        "name": "Laptop Backpack - 15.6 inch",
        "category": "bags_luggage",
        "price": 1699.00,
        "return_window_days": 15,
        "returnable": True,
    },
    "PROD-2010": {
        "product_id": "PROD-2010",
        "name": "Mechanical Keyboard - RGB",
        "category": "electronics",
        "price": 4599.00,
        "return_window_days": 10,
        "returnable": True,
    },
    "PROD-2011": {
        "product_id": "PROD-2011",
        "name": "Silk Saree - Handwoven",
        "category": "apparel",
        "price": 6499.00,
        "return_window_days": 5,
        "returnable": True,
    },
    "PROD-2012": {
        "product_id": "PROD-2012",
        "name": "Gift Card - \u20b91000 (Digital)",
        "category": "gift_cards",
        "price": 1000.00,
        "return_window_days": 0,
        "returnable": False,  # digital / non-physical, policy-excluded
    },
    # Newly launched item -- no orders reference it yet, useful for
    # testing "product exists but never ordered" paths
    "PROD-2013": {
        "product_id": "PROD-2013",
        "name": "Smart Fitness Band",
        "category": "electronics",
        "price": 1999.00,
        "return_window_days": 10,
        "returnable": True,
    },
}

# ---------------------------------------------------------------------------
# ORDERS
# ---------------------------------------------------------------------------
# status: one of "delivered", "shipped", "cancelled", "return_requested",
#         "return_completed"
# Dates are fixed (not relative to today) so results are reproducible run
# to run -- swap in `date.today()` arithmetic later if you want "live" data.
ORDERS = {
    "ORD-3001": {
        "order_id": "ORD-3001",
        "customer_id": "CUST-1001",
        "product_id": "PROD-2001",
        "quantity": 1,
        "price_paid": 2499.00,
        "order_date": "2026-07-01",
        "delivery_date": "2026-07-04",
        "status": "delivered",
    },
    "ORD-3002": {
        "order_id": "ORD-3002",
        "customer_id": "CUST-1001",
        "product_id": "PROD-2003",
        "quantity": 2,
        "price_paid": 1598.00,
        "order_date": "2026-06-10",
        "delivery_date": "2026-06-13",
        "status": "delivered",
    },
    "ORD-3003": {
        "order_id": "ORD-3003",
        "customer_id": "CUST-1002",
        "product_id": "PROD-2002",
        "quantity": 1,
        "price_paid": 3299.00,
        "order_date": "2026-07-20",
        "delivery_date": "2026-07-23",
        "status": "delivered",
    },
    "ORD-3004": {
        "order_id": "ORD-3004",
        "customer_id": "CUST-1002",
        "product_id": "PROD-2004",
        "quantity": 1,
        "price_paid": 599.00,
        "order_date": "2026-07-15",
        "delivery_date": "2026-07-18",
        "status": "delivered",
    },
    "ORD-3005": {
        "order_id": "ORD-3005",
        "customer_id": "CUST-1003",
        "product_id": "PROD-2005",
        "quantity": 1,
        "price_paid": 28999.00,
        "order_date": "2026-06-01",
        "delivery_date": "2026-06-05",
        "status": "delivered",
    },
    "ORD-3006": {
        "order_id": "ORD-3006",
        "customer_id": "CUST-1003",
        "product_id": "PROD-2006",
        "quantity": 1,
        "price_paid": 1899.00,
        "order_date": "2026-07-25",
        "delivery_date": "2026-07-27",
        "status": "return_requested",
    },
    "ORD-3007": {
        "order_id": "ORD-3007",
        "customer_id": "CUST-1004",
        "product_id": "PROD-2001",
        "quantity": 1,
        "price_paid": 2499.00,
        "order_date": "2026-07-30",
        "delivery_date": None,  # still in transit
        "status": "shipped",
    },
    "ORD-3008": {
        "order_id": "ORD-3008",
        "customer_id": "CUST-1004",
        "product_id": "PROD-2002",
        "quantity": 1,
        "price_paid": 3299.00,
        "order_date": "2026-05-01",
        "delivery_date": "2026-05-04",
        "status": "delivered",  # delivered long ago -- good for testing "window expired"
    },
    "ORD-3009": {
        "order_id": "ORD-3009",
        "customer_id": "CUST-1005",
        "product_id": "PROD-2007",
        "quantity": 3,
        "price_paid": 1047.00,
        "order_date": "2026-07-10",
        "delivery_date": "2026-07-12",
        "status": "delivered",  # perishable, non-returnable
    },
    "ORD-3010": {
        "order_id": "ORD-3010",
        "customer_id": "CUST-1005",
        "product_id": "PROD-2010",
        "quantity": 1,
        "price_paid": 4599.00,
        "order_date": "2026-07-28",
        "delivery_date": None,
        "status": "cancelled",  # cancelled before delivery
    },
    "ORD-3011": {
        "order_id": "ORD-3011",
        "customer_id": "CUST-1006",
        "product_id": "PROD-2008",
        "quantity": 1,
        "price_paid": 1199.00,
        "order_date": "2026-06-15",
        "delivery_date": "2026-06-18",
        "status": "return_completed",  # already returned & refunded
    },
    "ORD-3012": {
        "order_id": "ORD-3012",
        "customer_id": "CUST-1006",
        "product_id": "PROD-2009",
        "quantity": 1,
        "price_paid": 1699.00,
        "order_date": "2026-08-01",
        "delivery_date": "2026-08-02",  # next-day delivery
        "status": "delivered",
    },
    "ORD-3013": {
        "order_id": "ORD-3013",
        "customer_id": "CUST-1007",
        "product_id": "PROD-2011",
        "quantity": 1,
        "price_paid": 6499.00,
        "order_date": "2026-07-05",
        "delivery_date": "2026-07-05",  # same-day delivery
        "status": "delivered",
    },
    "ORD-3014": {
        "order_id": "ORD-3014",
        "customer_id": "CUST-1007",
        "product_id": "PROD-2012",
        "quantity": 1,
        "price_paid": 1000.00,
        "order_date": "2026-07-22",
        "delivery_date": "2026-07-22",  # digital, instant "delivery"
        "status": "delivered",  # non-returnable gift card
    },
    "ORD-3015": {
        "order_id": "ORD-3015",
        "customer_id": "CUST-1001",
        "product_id": "PROD-2010",
        "quantity": 1,
        "price_paid": 4599.00,
        "order_date": "2026-08-05",
        "delivery_date": "2026-08-08",  # delivered right at "today" for fresh-window tests
        "status": "delivered",
    },
    # NOTE: CUST-1008 (Karan Bose) has zero orders on purpose.
}


# ---------------------------------------------------------------------------
# Lookup / helper functions
# ---------------------------------------------------------------------------
# Plain functions for now. Later, wrap each of these as an @tool so the
# agent can call them directly instead of you passing raw dicts into a
# prompt.
def get_customer(customer_id: str) -> dict | None:
    """Look up a customer by ID. Returns None if not found."""
    return CUSTOMERS.get(customer_id)


def get_customer_by_username(username: str) -> dict | None:
    """Look up a customer by username. Returns None if not found."""
    for cust in CUSTOMERS.values():
        if cust["username"] == username:
            return cust
    return None


def verify_password(customer: dict, plaintext_password: str) -> bool:
    """Check a plaintext password attempt against a customer's stored hash."""
    if not customer or not plaintext_password:
        return False
    return check_password_hash(customer["password_hash"], plaintext_password)


def authenticate(identifier: str, plaintext_password: str) -> dict | None:
    """Try to log in with either a customer_id or a username plus password.

    Returns the customer dict on success, None on failure (unknown
    identifier OR wrong password -- deliberately the same result for
    both, so a login form can't be used to enumerate valid usernames).
    """
    identifier = (identifier or "").strip()
    customer = get_customer(identifier) or get_customer_by_username(identifier)
    if customer and verify_password(customer, plaintext_password):
        return customer
    return None


def get_product(product_id: str) -> dict | None:
    """Look up a product by ID. Returns None if not found."""
    return PRODUCTS.get(product_id)


def get_order(order_id: str) -> dict | None:
    """Look up an order by ID. Returns None if not found."""
    return ORDERS.get(order_id)


def get_orders_for_customer(customer_id: str) -> list[dict]:
    """Get all orders belonging to a given customer."""
    return [o for o in ORDERS.values() if o["customer_id"] == customer_id]


def check_return_eligibility(order_id: str, today: date | None = None) -> dict:
    """Check whether an order is eligible for return, and why/why not.
    Returns a dict like:
        {
            "eligible": bool,
            "reason": str,
            "order": dict | None,
            "product": dict | None,
        }
    """
    today = today or date.today()
    order = get_order(order_id)
    if order is None:
        return {"eligible": False, "reason": f"No order found with ID {order_id}.",
                "order": None, "product": None}
    product = get_product(order["product_id"])
    if product is None:
        return {"eligible": False, "reason": "Product record missing for this order.",
                "order": order, "product": None}
    if order["status"] not in ("delivered", "return_requested"):
        return {
            "eligible": False,
            "reason": f"Order status is '{order['status']}' -- only delivered "
                      f"orders can be returned.",
            "order": order,
            "product": product,
        }
    if order["status"] == "return_requested":
        return {
            "eligible": False,
            "reason": "A return has already been requested for this order.",
            "order": order,
            "product": product,
        }
    if not product["returnable"]:
        return {
            "eligible": False,
            "reason": f"'{product['name']}' is not returnable "
                      f"(category: {product['category']}).",
            "order": order,
            "product": product,
        }
    delivery_date = date.fromisoformat(order["delivery_date"])
    window_end = delivery_date + timedelta(days=product["return_window_days"])
    if today > window_end:
        return {
            "eligible": False,
            "reason": f"Return window expired on {window_end.isoformat()} "
                      f"({product['return_window_days']} days after delivery).",
            "order": order,
            "product": product,
        }
    return {
        "eligible": True,
        "reason": f"Eligible for return until {window_end.isoformat()}.",
        "order": order,
        "product": product,
    }


def process_return(order_id: str) -> dict:
    """Actually process a return: marks the order as 'return_requested'.
    This mutates ORDERS in place (in-memory only -- resets when the
    script restarts). This is deliberately a separate function from
    check_return_eligibility -- checking eligibility should never have
    side effects, only this function does.
    Returns a dict like:
        {"success": bool, "message": str}
    """
    order = get_order(order_id)
    if order is None:
        return {"success": False, "message": f"No order found with ID {order_id}."}
    if order["status"] != "delivered":
        return {
            "success": False,
            "message": f"Cannot process return -- order status is "
                       f"'{order['status']}', not 'delivered'.",
        }
    order["status"] = "return_requested"
    return {
        "success": True,
        "message": f"Return processed for {order_id}. Status updated to "
                   f"'return_requested'.",
    }


# ---------------------------------------------------------------------------
# Quick sanity check when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Loaded {len(CUSTOMERS)} customers, {len(PRODUCTS)} products, "
          f"{len(ORDERS)} orders.\n")

    print("Login sanity check:")
    for username, pw in TEST_LOGINS.items():
        ok = authenticate(username, pw) is not None
        bad = authenticate(username, "wrong-password") is not None
        print(f"  {username}: correct password -> {ok}, wrong password -> {bad}")

    test_cases = [
        ("ORD-3001", date(2026, 7, 8)),   # within window
        ("ORD-3001", date(2026, 8, 1)),   # window expired
        ("ORD-3004", date(2026, 7, 19)),  # non-returnable category
        ("ORD-3006", date(2026, 7, 28)),  # already return_requested
        ("ORD-3007", date(2026, 8, 1)),   # not yet delivered
        ("ORD-9999", date(2026, 8, 1)),   # doesn't exist
        ("ORD-3009", date(2026, 7, 13)),  # perishable, non-returnable
        ("ORD-3010", date(2026, 7, 29)),  # cancelled order
        ("ORD-3011", date(2026, 6, 20)),  # already return_completed
        ("ORD-3013", date(2026, 7, 8)),   # same-day delivery, short window
        ("ORD-3014", date(2026, 7, 23)),  # non-returnable gift card
        ("ORD-3015", date(2026, 8, 10)),  # freshly delivered, well within window
    ]
    print("\nEligibility sanity check:")
    for order_id, as_of in test_cases:
        result = check_return_eligibility(order_id, today=as_of)
        print(f"{order_id} (as of {as_of}): "
              f"{'ELIGIBLE' if result['eligible'] else 'NOT ELIGIBLE'} "
              f"-- {result['reason']}")