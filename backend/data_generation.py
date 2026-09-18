import os
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Variables that will be used to generate the data
# More advance model might require more variables such as seller ratings and shipping costs
class SellerListing(BaseModel):
    seller_name: str = Field(description="Name of the seller")
    condition: str = Field(description="e.g. Mint, Near Mint, Very Good, Fair")
    price: float = Field(description="Asking price in USD")

class CollectibleProduct(BaseModel):
    item_name: str
    category: str
    brand: str
    estimated_market_value: float
    listings: list[SellerListing]

def get_marketplace_data(query: str) -> CollectibleProduct:
    prompt = f"""
    Generate realistic marketplace listings for the collectible item: "{query}".
    Provide between 4 to 6 different sellers with varying prices and conditions 
    typical for collectors (Mint, Very Good, Fair).
    """
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": CollectibleProduct,
            "temperature": 0.7,  # Slightly higher temperature creates price/condition variation
        },
    )

    return response.parsed



