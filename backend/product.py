import json
import os

# Products are kept in memory during runtime and persisted to a JSON file.
products = []
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "products.json")


def ensure_storage_dir():
    # Create the shared data directory before reading or writing files.
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)


def save_products():
    # Persist the current collection so it survives application restarts.
    ensure_storage_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=2)


def load_products():
    # Load the collection from disk; invalid or missing data becomes an empty list.
    global products
    ensure_storage_dir()
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            try:
                loaded = json.load(file)
                if isinstance(loaded, list):
                    products = loaded
                    return products
            except json.JSONDecodeError:
                pass

    products = []
    return products


def seed_default_products():
    # Initialize storage without restoring deleted products or hard-coded defaults.
    ensure_storage_dir()
    if os.path.exists(DATA_FILE):
        load_products()
        return products

    products.clear()
    save_products()
    return products


def add_product(name, purchase_price, current_price, inventory_id, brand, category, series):
    # Build a product record, store it in memory, and persist it immediately.
    product = {
        "id": len(products) + 1,
        "name": name,
        "purchase_price": purchase_price,
        "current_price": current_price,
        "inventory_id": inventory_id,
        "brand": brand,
        "category": category,
        "series": series
    }

    products.append(product)
    save_products()
    return product


def get_products():
    # Return the current collection exactly as stored in memory.
    return products


def get_product(product_id):
    # Return one product by ID, or None when it does not exist.
    for product in products:
        if product["id"] == product_id:
            return product

    return None