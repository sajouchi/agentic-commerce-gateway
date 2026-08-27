import random
from typing import List

from faker import Faker
import pandas as pd

from app.db.sellerDatabase import fetch_oneColumn, insertDatabase,sellerDatabase, simple_fetchAll
from app.db.sellerPolicies import insert_itemPolicy
from app.core.embeddingFunctions import embedContent
from app.schema.allSchema import discount_tier

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

def populate_sellerDatabase(amt:int,csv:bool=False):
    entries = genFakeEntries(amt=amt)
    for entry in entries:
        insertDatabase(**entry)
      
    if csv:  
        result = simple_fetchAll()
        rows_list= []

        for entry in result:    
            
            entry_df = {"sku":entry.sku,
                        "item":entry.item,
                        "price_base":entry.price_base,
                        "description":entry.description,
                        "min_order_qty":entry.min_order_qty,
                        "stock_quantity":entry.stock_quantity,
                        "category":entry.category,
                        "company":entry.company,
                        "location_availability":entry.location_availability} # not include the vector embeddings 
            
        rows_list.append(entry_df)
        
        try:
            df = pd.DataFrame(data=rows_list)
            df.to_csv("mock_data.csv",index=False)
            print("saved <mock_data.csv> file!")
        except Exception as e:
            print(f"error :- {e}")
            
def populate_sellerPolicies():
    """
        function to populate the seller policis for each 'sku' item in database.
    """
    all_sku = fetch_oneColumn("sku")
    min_quantity =  fetch_oneColumn("min_order_qty")

    min = [10,20,45]
    values = [5,8,15]
    
    dis_tiers:List[discount_tier] = []
    
    for m,v in zip(min,values):
        temp = discount_tier(min_qty=m,value=v)
        dis_tiers.append(temp)
    
    dis_tiers = [dis.model_dump() for dis in dis_tiers]
    
    for sku,min_qty in zip(all_sku,min_quantity,strict=True):
        insert_itemPolicy(sku=sku,min_order_qty=min_qty,
                          absolute_min_price=random.randint(15,130),
                          discount_tiers=dis_tiers)

    print("Entered pollicies into db!")

### main function ##
def fake_data_gen(amt:int) -> bool:
    """
    Generates argumented amount of fake data for item,
    Which gets saved to both policies and item database.

    Args:
        amt (int): the numbers of fake items data.
    Returns:
        bool value, 'True' for successfull generation and entry, 
        while 'False' for failure.
    """ 
    try:
        populate_sellerDatabase(amt=amt)
        populate_sellerPolicies()
        return True
    except Exception as e:
        return False
    
    