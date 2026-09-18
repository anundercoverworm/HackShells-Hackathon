from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend import data_generation, inventories, prices, product

# Load optional environment settings such as the OpenAI API key.
load_dotenv(dotenv_path="../.env")

# FastAPI application exposed to the Streamlit frontend.
app = FastAPI(title="Collection Tracker API")

# Allow local frontend clients to call the API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductCreate(BaseModel):
    # Request body used when adding a product to the collection.
    name: str
    series: str = "General"
    purchase_price: float = 0.0
    current_price: float | None = None
    inventory_id: int = 1
    brand: str = "Unknown"
    category: str = "Collectible"


class SeriesCreate(BaseModel):
    # Request body used when creating a collection series.
    name: str


class PriceUpdate(BaseModel):
    # Request body used when updating a product's user-recorded price.
    price: float


# Load persisted products and create the initial inventory at startup.
product.seed_default_products()
inventories.seed_default_inventory()


def ensure_price_history(product_id: int):
    # Reuse valid history and rebuild it when it is missing or inconsistent.
    item = product.get_product(product_id)
    if item is None:
        return []

    history = prices.get_price_history(product_id)
    if history and prices.is_history_valid(product_id):
        return history

    prices.clear_history(product_id)
    current_price = item.get("current_price", item.get("purchase_price", 0))
    for entry in prices.build_realistic_history(product_id, current_price):
        prices.price_history.append(entry)

    return prices.get_price_history(product_id)


# Ensure every product loaded at startup has usable price-history data.
for item in product.get_products():
    ensure_price_history(item["id"])


@app.get("/api/health")
def health():
    # Lightweight endpoint used by the launcher to detect backend readiness.
    return {"message": "Hello API"}


@app.get("/api/products")
def get_products():
    # Return the complete persisted collection.
    return product.get_products()


@app.get("/api/products/{product_id}")
def get_product_by_id(product_id: int):
    # Return one product or a standard HTTP 404 response.
    item = product.get_product(product_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return item


@app.post("/api/products")
def create_product(item: ProductCreate):
    # Validate, persist, and initialize history for a new product.
    name = item.name.strip()
    series = item.series.strip() or "General"

    if not name:
        raise HTTPException(status_code=400, detail="Product name is required")

    current_price = item.current_price if item.current_price is not None else item.purchase_price

    new_product = product.add_product(
        name=name,
        purchase_price=item.purchase_price,
        current_price=current_price,
        inventory_id=item.inventory_id,
        brand=item.brand,
        category=item.category,
        series=series,
    )
    ensure_price_history(new_product["id"])
    return new_product


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int):
    # Delete the product and its associated price history together.
    products = product.get_products()
    for index, item in enumerate(products):
        if item["id"] == product_id:
            removed = products.pop(index)
            product.save_products()
            prices.clear_history(product_id)
            return {"message": "Product removed", "product": removed}

    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/api/products/{product_id}/price")
def update_product_price(product_id: int, payload: PriceUpdate):
    # Update the user price while keeping its history consistent.
    updated = prices.add_price(product_id, payload.price)
    if updated is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated


@app.get("/api/products/{product_id}/price-history")
def get_product_price_history(product_id: int):
    # Return validated history for one product.
    item = product.get_product(product_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return ensure_price_history(product_id)


@app.get("/api/series")
def get_series():
    # Return unique series names currently used by products.
    series = sorted({item["series"] for item in product.get_products()})
    return series


@app.post("/api/series")
def create_series(item: SeriesCreate):
    # Validate a series name and report whether it already exists.
    series_name = item.name.strip()
    if not series_name:
        raise HTTPException(status_code=400, detail="Series name is required")

    existing = {entry["series"].lower() for entry in product.get_products()}
    if series_name.lower() in existing:
        return {"message": "Series already exists", "name": series_name}

    return {"message": "Series created", "name": series_name}


@app.get("/api/inventories")
def get_inventories():
    # Return the available inventories.
    return inventories.get_inventories()


@app.get("/api/inventories/{inventory_id}")
def get_inventory_by_id(inventory_id: int):
    # Return one inventory or a standard HTTP 404 response.
    item = inventories.get_inventory(inventory_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return item


@app.get("/api/inventories/{inventory_id}/value")
def get_inventory_value_inventory(inventory_id: int):
    # Return the total current value of products in an inventory.
    inventory = inventories.get_inventory(inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return {"inventory_id": inventory_id, "total_value": inventories.get_inventory_value(inventory_id)}


@app.get("/api/marketplace/{item_name}")
def get_marketplace(item_name: str):
    # Return marketplace listings based on the product's current price.
    normalized = item_name.strip().lower()
    product_match = next(
        (item for item in product.get_products() if item["name"].strip().lower() == normalized),
        None,
    )
    base_value = product_match.get("current_price", 100.0) if product_match else 100.0
    item_data = data_generation.get_item_data(item_name, base_value=base_value)
    return [entry.model_dump() for entry in item_data]


@app.get("/api/marketplace/{item_name}/history")
def get_marketplace_history(item_name: str):
    # Return synthetic market history for the selected product.
    normalized = item_name.strip().lower()
    product_match = next(
        (item for item in product.get_products() if item["name"].strip().lower() == normalized),
        None,
    )
    base_value = product_match.get("current_price", 100.0) if product_match else 100.0
    history = data_generation.get_market_history(item_name, base_value=base_value)
    return [entry.model_dump() for entry in history]


@app.get("/api/hello")
def hello():
    # Simple connectivity endpoint for manual checks.
    return {"message": "Backend connected"}
