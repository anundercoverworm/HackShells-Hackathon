products = []


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
    return product


def get_products():
    return products


def get_product(product_id):
    for product in products:
        if product["id"] == product_id:
            return product

    return None