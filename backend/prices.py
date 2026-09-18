import json
import os
from datetime import datetime, timedelta

from backend import product

# Price history is cached in memory and synchronized with a JSON file.
price_history = []
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "price_history.json")


def ensure_storage_dir():
    # Make sure the data directory exists before accessing the history file.
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)


def save_history():
    # Persist all recorded price-history entries.
    ensure_storage_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(price_history, file, ensure_ascii=False, indent=2)


def load_history():
    # Restore saved history, falling back to an empty history on invalid data.
    global price_history
    ensure_storage_dir()
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            try:
                loaded = json.load(file)
                if isinstance(loaded, list):
                    price_history = loaded
                    return price_history
            except json.JSONDecodeError:
                pass
    price_history = []
    return price_history


def clear_history(product_id):
    # Remove every history entry belonging to one product.
    global price_history
    price_history = [entry for entry in price_history if entry["product_id"] != product_id]
    save_history()


def is_history_valid(product_id):
    # Reject missing, malformed, or implausible history before rebuilding it.
    history = get_price_history(product_id)
    if not history:
        return False

    product_data = product.get_product(product_id)
    if product_data is None:
        return False

    current_price = float(product_data.get("current_price", product_data.get("purchase_price", 0) or 0))
    prices = [float(entry["price"]) for entry in history]

    if not prices:
        return False

    if len(history) < 5 or len(history) > 9:
        return False

    if current_price > 0:
        min_price = min(prices)
        max_price = max(prices)
        if max_price > current_price * 2.0 or min_price < current_price * 0.6:
            return False

    return True


def build_realistic_history(product_id, current_price):
    # Create a seven-day history tied to the user's recorded product price.
    product_data = product.get_product(product_id)
    if product_data is None:
        return []

    current_price = float(current_price or product_data.get("purchase_price", 100.0) or 100.0)
    start_date = datetime.now().date() - timedelta(days=6)
    fixed_price = round(current_price, 2)

    history = []
    for offset in range(7):
        day = start_date + timedelta(days=offset)
        history.append({
            "product_id": product_id,
            "price": fixed_price,
            "date": day.isoformat(),
        })

    return history


def add_history_entry(product_id, price):
    # Append one timestamped price observation for an existing product.
    product_data = product.get_product(product_id)
    if product_data is None:
        return None

    price_entry = {
        "product_id": product_id,
        "price": float(price),
        "date": datetime.now().isoformat(),
    }

    price_history.append(price_entry)
    save_history()
    return price_entry


def add_price(product_id, price):
    # Update the user's current price and rebuild its consistent history.
    product_data = product.get_product(product_id)
    if product_data is None:
        return None

    product_data["current_price"] = float(price)
    clear_history(product_id)
    for entry in build_realistic_history(product_id, float(price)):
        price_history.append(entry)
    save_history()
    return product_data


def get_price_history(product_id):
    # Load history lazily and return only entries for the requested product.
    if not price_history:
        load_history()
    history = []
    for entry in price_history:
        if entry["product_id"] == product_id:
            history.append(entry)
    return history


def get_current_price(product_id):
    # Return the current user-recorded price for one product.
    product_data = product.get_product(product_id)

    if product_data is None:
        return None

    return product_data["current_price"]


def get_price_graph(product_id):
    # Convert stored history into the simple shape expected by graph consumers.
    history = get_price_history(product_id)

    graph_data = []

    for entry in history:
        graph_data.append({
            "date": entry["date"],
            "price": entry["price"],
        })

    return graph_data