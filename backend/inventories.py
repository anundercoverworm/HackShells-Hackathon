inventories = []


def seed_default_inventory():
    if inventories:
        return inventories

    inventories.extend([
        {"id": 1, "name": "Main Inventory"},
        {"id": 2, "name": "Wishlist"},
    ])
    return inventories


def add_inventory(name):
    inventory = {
        "id": len(inventories) + 1,
        "name": name,
    }

    inventories.append(inventory)
    return inventory


def get_inventories():
    if not inventories:
        seed_default_inventory()
    return inventories


def get_inventory(inventory_id):
    for inventory in inventories:
        if inventory["id"] == inventory_id:
            return inventory

    return None


def get_inventory_value(inventory_id):
    total = 0

    from backend import product

    for item in product.get_products():
        if item["inventory_id"] == inventory_id:
            total += item["current_price"]

    return total