from dotenv import load_dotenv
import os
load_dotenv(dotenv_path="../.env")

import data_generation
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"message": "Hello API"}

data = data_generation.get_marketplace_data("1999 Holographic Charizard 1st Edition")
print(f"Product: {data.item_name} (Est. Value: ${data.estimated_market_value})")
for listing in data.listings:
    print(f"- {listing.seller_name}: ${listing.price} [{listing.condition}]")