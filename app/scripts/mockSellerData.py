import random
from typing import List

from faker import Faker

from app.db.sellerDatabase import insertDatabase,sellerDatabase
from app.db.sellerPolicies import insert_itemPolicy
from app.core.embeddingFunctions import embedContent

Faker.seed(42)
fake = Faker()

# class sellerDatabase(SQLModel,table=True):
#     sku:int = Field(primary_key=True)
#     item:str = Field(nullable=False)
#     category:str
#     company:str
#     price_base:int
#     min_order_qty:int 
#     stock_quantity:int 
#     location_availability:str
#     vector_embedding: list[float] = Field(sa_type=VECTOR(VECTOR_DIMENSIONS)) # set dimension size according the model output size

categories = ["Electronics", "Executive Stationery", "Drinkware", "Travel Accessories"]
locations_available = ["New York, USA","San Francisco, USA","London, UK"]

electronics = [
    "MagSafe Power Bank",
    "ANC Headphones",
    "Multi-Port Desk Hub",
    "Bluetooth Conference Speaker",
    "Wireless Charging Mousepad",
    "Foldable Solar Panel Charger",
    "Smart Smartwatch Dock",
    "UVC Sterilizer Desk Box",
    "Mini DLP Pocket Projector",
    "Noise-Canceling Wireless Earbuds",
]

executive_stationery = [
    "Leather Bound Journal",
    "Brass Rollerball Pen Set",
    "Smart Daily Planner",
    "Minimalist Desk Organizer",
    "Engraved Executive Portfolio",
    "Hardcover Grid Dot Notebook",
    "Executive Stylus Pen for Tablets",
    "Refillable Leather Binder",
    "Aluminum Business Card Case",
    "Monogrammed Wax Seal Stamp Kit",
]

drinkware = [
    "Vacuum Insulated Thermal Tumbler",
    "Smart Temperature Control Mug",
    "Copper Infused Flask",
    "Double-Wall Espresso Glass Set",
    "Stainless Steel Water Bottle",
    "Insulated Stainless Steel Can Cooler",
    "Ceramic Travel Coffee Press",
    "Foldable Silicon Water Bottle",
    "Whiskey Decanter & Glass Set",
    "Infuser Fruit Water Pitcher",
]

travel_accessories = [
    "Waterproof Tech Organizer Case",
    "Genuine Leather Passport Holder",
    "Expandable Garment Bag",
    "TSA-Approved Luggage Lock",
    "Padded Memory Foam Travel Pillow",
    "RFID Blocking Leather Wallet",
    "Packable Lightweight Backpack",
    "Universal Travel Plug Adapter",
    "Compression Packing Cubes Set",
    "Toiletry Hanging Organizer",
]

def genFakeEntries(amt:int) -> List[dict]:
    product_entries = []
    
    for _ in range(amt):
        category = random.choice(categories)
        locations = str(f"{random.choice(locations_available)}")
        company = fake.company()
        
        if category == "Electronics":
            item = f"{random.choice(electronics)}"
            description = f"item - {item}, category - {category}"
        elif category == "Executive Stationery":
            item = f"{random.choice(electronics)}"
            description = f"item - {item}, category - {category}"
        elif category == "Drinkware":
            item = f"{random.choice(electronics)}"
            description = f"item - {item}, category - {category}"
        else:
            item = f"{random.choice(['Tech Organizer', 'Leather Passport Holder', 'Garment Bag'])}"
            description = f"item - {item}, category - {category}"

        sku = f"GIFT-{random.randint(10000, 99999)}"
        price_base = random.randint(15,250)
        stock_quantity = random.randint(100,799)
        min_order_qty = random.randint(5,89)
        
        entry = sellerDatabase(sku=sku,item=item,description=description,
                              category=category,company=company,
                              price_base=price_base,
                              min_order_qty=min_order_qty,
                              stock_quantity=stock_quantity,
                              location_availability=locations)
        
        embed_of_entry = embedContent(entry.model_dump_json(include=["description"]))
        
        product_entries.append(entry.model_dump() | {"vector_embedding":embed_of_entry})
    
    return product_entries