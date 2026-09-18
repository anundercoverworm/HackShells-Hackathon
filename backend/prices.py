from datetime import datetime
from backend import product

price_history = []


def add_price(product_id, price):
    product_data = product.get_product(product_id)

    if product_data is None:
        return None

    product_data["current_price"] = price

    price_entry = {
        "product_id": product_id,
        "price": price,
        "date": datetime.now().isoformat()
    }

    price_history.append(price_entry)
    return price_entry


def get_price_history(product_id):
    history = []

    for entry in price_history:
        if entry["product_id"] == product_id:
            history.append(entry)

    return history


def get_current_price(product_id):
    product_data = product.get_product(product_id)

    if product_data is None:
        return None

    return product_data["current_price"]

def get_price_graph(product_id):
    history = get_price_history(product_id)

    graph_data = []

    for entry in history:
        graph_data.append({
            "date": entry["date"],
            "price": entry["price"]
        })

    return graph_data