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

# Generates seller data for prompted item across 4 days
# Allows market value to be graphed over time to see how it changes
item = data_generation.get_item_data("1999 Holographic Charizard 1st Edition")

print(f"Product: {item[0].item_name} (Current Est. Value: ${item[3].estimated_market_value})")
print("\n")
print(f"Curent Sellers:")
for listing in item[3].listings:
    print(f"- ${listing.price} [{listing.condition}]")
print(f"Est. Market Value Over 4 Days:")
print(f"3 days ago - ${item[0].estimated_market_value}")
print(f"2 days ago - ${item[1].estimated_market_value}")
print(f"1 day ago - ${item[2].estimated_market_value}")
print(f"Today - ${item[3].estimated_market_value}")