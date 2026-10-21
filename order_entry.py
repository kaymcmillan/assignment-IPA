"""
order_entry.py
Create and verify customer orders using Python and the Supabase API.

This program uses only Python's built-in libraries, so nothing needs to be installed.
Run with:  python order_entry.py
"""
import json
import os
import urllib.error
import urllib.request
from datetime import date


# ---------- Setup: read credentials from the .env file ----------

def load_env_file():
    """Read KEY=VALUE lines from the .env file that sits next to this script."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


def get_credentials():
    load_env_file()
    url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    key = os.getenv("SUPABASE_KEY", "").strip()
    if not url or not key or "your-" in url or "your-" in key:
        raise SystemExit("Missing SUPABASE_URL or SUPABASE_KEY. Check your .env file.")
    if not url.startswith("https://"):
        raise SystemExit("SUPABASE_URL should start with https://")
    return url, key


class Database:
    """Small helper that sends requests to the Supabase REST API."""

    def __init__(self, url, key):
        self.base = url + "/rest/v1/"
        self.headers = {"apikey": key, "Content-Type": "application/json"}
        if key.startswith("eyJ"):  # older-style keys are also sent as a bearer token
            self.headers["Authorization"] = "Bearer " + key

    def _send(self, request):
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))

    def select(self, table, query):
        """Get rows from a table. Example query: 'select=*&order=customer_id.asc'"""
        request = urllib.request.Request(self.base + table + "?" + query,
                                         headers=self.headers, method="GET")
        return self._send(request)

    def insert(self, table, row):
        """Insert one row and return the saved row (including the new order_id)."""
        headers = dict(self.headers)
        headers["Prefer"] = "return=representation"
        request = urllib.request.Request(self.base + table,
                                         data=json.dumps(row).encode("utf-8"),
                                         headers=headers, method="POST")
        return self._send(request)


# ---------- Part 1: Display customers and products ----------

def show_customers(customers):
    print("\nCUSTOMERS")
    print(f"{'ID':<6}{'Name':<25}{'Email':<35}{'City':<20}")
    print("-" * 86)
    for c in customers:
        print(f"{c['customer_id']:<6}{c['name']:<25}{c['email']:<35}{c['city']:<20}")


def show_products(products):
    print("\nPRODUCTS")
    print(f"{'ID':<6}{'Product':<30}{'Category':<20}{'Price':>10}")
    print("-" * 66)
    for p in products:
        price = f"${float(p['price']):,.2f}"
        print(f"{p['product_id']:<6}{p['product_name']:<30}{p['category']:<20}{price:>10}")


# ---------- Part 2: Collect and validate input ----------

def ask_for_id(prompt, valid_ids, label):
    """Keep asking until the user types a whole number that exists in valid_ids."""
    while True:
        text = input(prompt).strip()
        try:
            value = int(text)
        except ValueError:
            print(f"'{text}' is not a valid {label} ID. Please enter a whole number like 1 or 2.")
            continue
        if value not in valid_ids:
            print(f"No {label} found with ID {value}. Please choose an ID from the table above.")
            continue
        return value


def ask_for_quantity():
    """Keep asking until the user types a positive whole number."""
    while True:
        text = input("Enter quantity: ").strip()
        try:
            value = int(text)
        except ValueError:
            print(f"'{text}' is not a valid quantity. Please enter a positive whole number.")
            continue
        if value <= 0:
            print("Quantity must be greater than zero.")
            continue
        return value


# ---------- Part 3: Confirm and save ----------

def confirm_order(customer, product, quantity):
    """Show a summary and ask Y/N. Returns True for Y, False for N."""
    price = float(product["price"])
    print("\nORDER SUMMARY")
    print(f"  Customer:   {customer['name']}")
    print(f"  Product:    {product['product_name']}")
    print(f"  Quantity:   {quantity}")
    print(f"  Unit price: ${price:,.2f}")
    print(f"  Total:      ${quantity * price:,.2f}")

    while True:
        answer = input("\nConfirm this order? (Y/N): ").strip().upper()
        if answer == "Y":
            return True
        if answer == "N":
            return False
        print("Please enter Y or N.")


def save_order(db, customer_id, product, quantity):
    """Insert the order. Returns the new order_id, or None if it failed."""
    new_row = {
        "customer_id": customer_id,
        "product_id": product["product_id"],
        "quantity": quantity,
        "order_date": date.today().isoformat(),
        "unit_price": float(product["price"]),  # price comes from the database
    }  # order_id is NOT sent; the database generates it
    try:
        saved = db.insert("orders", new_row)
        if not saved:
            print("The order could not be saved. Please try again.")
            return None
        order_id = saved[0]["order_id"]
        print(f"\nOrder saved successfully! Order ID: {order_id}")
        return order_id
    except urllib.error.HTTPError as error:
        print(f"Sorry, the order could not be saved (error code {error.code}). Please try again later.")
        return None
    except Exception:
        print("Sorry, there was a problem saving the order. Please try again later.")
        return None


# ---------- Main program ----------

def main():
    url, key = get_credentials()
    db = Database(url, key)

    try:
        customers = db.select("customers", "select=*&order=customer_id.asc")
        products = db.select("products", "select=*&order=product_id.asc")
    except urllib.error.HTTPError as error:
        print(f"Supabase answered with an error (code {error.code}).")
        print("Details:", error.read().decode("utf-8", errors="replace"))
        return
    except urllib.error.URLError as error:
        print("Could not reach Supabase. Reason:", error.reason)
        return
    except Exception as error:
        print("Unexpected problem:", error)
        return

    customers_by_id = {c["customer_id"]: c for c in customers}
    products_by_id = {p["product_id"]: p for p in products}

    show_customers(customers)
    show_products(products)
    print()

    customer_id = ask_for_id("Enter customer ID: ", customers_by_id, "customer")
    product_id = ask_for_id("Enter product ID: ", products_by_id, "product")
    quantity = ask_for_quantity()

    customer = customers_by_id[customer_id]
    product = products_by_id[product_id]

    if not confirm_order(customer, product, quantity):
        print("Order cancelled. Nothing was saved.")
        return

    order_id = save_order(db, customer_id, product, quantity)
    if order_id is not None:
        print("Next step: we will retrieve and display this saved order.")


if __name__ == "__main__":
    main()