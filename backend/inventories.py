# In-memory inventory registry used by the API and dashboard.
inventories = []


def seed_default_inventory():
    # Create the initial inventory only when the registry has not been populated.
    if inventories:
        return inventories

    inventories.extend([
        {"id": 1, "name": "Main Inventory"},
    ])
    return inventories


def add_inventory(name):
    # Assign the next sequential identifier and keep the new inventory in memory.
    inventory = {
        "id": len(inventories) + 1,
        "name": name,
    }

    inventories.append(inventory)
    return inventory


def get_inventories():
    # Ensure the API always has the initial inventory available.
    if not inventories:
        seed_default_inventory()
    return inventories


def get_inventory(inventory_id):
    # Find one inventory by its public identifier.
    for inventory in inventories:
        if inventory["id"] == inventory_id:
            return inventory

    return None


def get_inventory_value(inventory_id):
    # Calculate the value of products assigned to this inventory.
    total = 0

    from backend import product

    for item in product.get_products():
        if item["inventory_id"] == inventory_id:
            total += item["current_price"]

    return total