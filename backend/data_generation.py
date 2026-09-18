import math
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


class SellerListing(BaseModel):
    condition: str = Field(description="e.g. Mint, Near Mint, Very Good, Fair")
    price: float = Field(description="Asking price in USD")


class CollectibleProduct(BaseModel):
    item_name: str
    category: str
    brand: str
    estimated_market_value: float
    listings: list[SellerListing]


class MarketHistoryPoint(BaseModel):
    date: str
    estimated_market_value: float


def get_marketplace_data(query: str, price: float, variation: float = 0.0) -> CollectibleProduct:
    base_value = float(price) if price != -1 else 100.0
    adjusted_value = round(base_value * (1 + variation), 2)

    if client is None:
        return CollectibleProduct(
            item_name=query,
            category="Collectible",
            brand="Unknown",
            estimated_market_value=adjusted_value,
            listings=[
                SellerListing(condition="Mint", price=adjusted_value * 1.08),
                SellerListing(condition="Near Mint", price=adjusted_value * 1.02),
                SellerListing(condition="Very Good", price=adjusted_value * 0.96),
                SellerListing(condition="Fair", price=adjusted_value * 0.88),
            ],
        )

    prompt = f"""
    Generate marketplace listings for the collectible item: "{query}".
    Provide between 4 to 6 different sellers with varying prices and conditions typical for collectors
    (Mint, Very Good, Fair). Use an estimated market value around ${adjusted_value:,.2f} USD,
    and make it realistic for a collectible market trend.
    """
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful e-commerce mock data generator."},
            {"role": "user", "content": prompt},
        ],
        response_format=CollectibleProduct,
        temperature=0.8,
    )

    return response.choices[0].message.parsed


def get_market_history(query: str, base_value: float = 100.0) -> list[MarketHistoryPoint]:
    if base_value <= 0:
        base_value = 100.0

    start_date = datetime.now().date() - timedelta(days=6)
    realistic_changes = [-0.08, -0.04, 0.02, 0.06, 0.04, -0.02, 0.07]

    history = []
    for offset, variation in enumerate(realistic_changes):
        day = start_date + timedelta(days=offset)
        seasonal_wave = 0.012 * math.sin((offset + 1) * 1.5)
        value = base_value * (1 + variation + seasonal_wave)
        value = round(max(base_value * 0.85, value), 2)
        history.append(MarketHistoryPoint(date=day.isoformat(), estimated_market_value=value))

    history[-1] = MarketHistoryPoint(
        date=history[-1].date,
        estimated_market_value=round(base_value * 1.07, 2),
    )

    return history


def get_item_data(query: str, base_value: float | None = None) -> list[CollectibleProduct]:
    base_value = float(base_value) if base_value is not None else 100.0
    variations = [-0.09, -0.04, 0.05, 0.11]

    item_data = []
    for variation in variations:
        item_data.append(get_marketplace_data(query, base_value, variation))

    return item_data

