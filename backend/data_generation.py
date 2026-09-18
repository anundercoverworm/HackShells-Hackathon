import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Variables that will be used to generate the data
# More advance model might require more variables such as seller ratings and shipping costs
class SellerListing(BaseModel):
    condition: str = Field(description="e.g. Mint, Near Mint, Very Good, Fair")
    price: float = Field(description="Asking price in USD")

class CollectibleProduct(BaseModel):
    item_name: str
    category: str
    brand: str
    estimated_market_value: float
    listings: list[SellerListing]

def get_marketplace_data(query: str, price: float) -> CollectibleProduct:
    prompt = f"""
    Generate marketplace listings for the collectible item: "{query}".
    Provide between 4 to 6 different sellers with varying prices and conditions 
    typical for collectors (Mint, Very Good, Fair) If {price} is not "-1", have the estimated market
    value be similar to that price (but not the same).
    """
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini", # Use the mini model to save costs during your hackathon
        messages=[
            {"role": "system", "content": "You are a helpful e-commerce mock data generator."},
            {"role": "user", "content": prompt}
        ],
        response_format=CollectibleProduct,
        temperature=0.8,
    )

    return response.choices[0].message.parsed

def get_item_data(query: str) -> list[CollectibleProduct]:

    item_data = []
    item_data.append(get_marketplace_data(query, -1))
    for i in range(3):
        item_data.append(get_marketplace_data(query, item_data[0].estimated_market_value))

    return item_data



