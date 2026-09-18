import json
import os

products = []
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "products.json")


def ensure_storage_dir():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)


def save_products():
    ensure_storage_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=2)


def load_products():
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
    ensure_storage_dir()
    if os.path.exists(DATA_FILE):
        load_products()
        return products

    products.clear()
    save_products()
    return products


def add_product(name, purchase_price, current_price, inventory_id, brand, category, series):
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
    return products


def get_product(product_id):
    for product in products:
        if product["id"] == product_id:
            return product

    return None