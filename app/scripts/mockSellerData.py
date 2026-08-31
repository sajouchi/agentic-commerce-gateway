import random
from typing import List

from faker import Faker
import pandas as pd

from app.db.sellerDatabase import (fetch_oneColumn, insertDatabase,
                                  SellerDatabase, simple_fetchAll)
from app.db.sellerPolicies import insert_itemPolicy
from app.core.embedding_generator import embedContent
from app.schema.allSchema import DiscountTier

Faker.seed(42)
fake = Faker()

# class sellerDatabase(SQLModel,table=True):
#     sku:int = Field(primary_key=True)
#     item:str = Field(nullable=False)
#     category:str
#     company:str
#     pricebase:int
#     minorderqty:int 
#     stockquantity:int 
#     locationavailability:str
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
        pricebase = random.randint(15,250)
        stockquantity = random.randint(100,799)
        minorderqty = random.randint(5,89)
        
        entry = SellerDatabase(sku=sku,item=item,description=description,
                              category=category,company=company,
                              pricebase=pricebase,
                              minorderqty=minorderqty,
                              stockquantity=stockquantity,
                              locationavailability=locations)
        
        embed_of_entry = embedContent(entry.model_dump_json(include=["description"]))
        
        product_entries.append(entry.model_dump() | {"vectorembeddings":embed_of_entry})
    
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
                        "pricebase":entry.pricebase,
                        "description":entry.description,
                        "minorderqty":entry.minorderqty,
                        "stockquantity":entry.stockquantity,
                        "category":entry.category,
                        "company":entry.company,
                        "locationavailability":entry.locationavailability} # not include the vector embeddings 
            
            rows_list.append(entry_df)
        
        try:
            df = pd.DataFrame(data=rows_list)
            df.to_csv("mock_data.csv",index=False)
            print("saved sellers products mock data to <sellerData.csv>!")
        except Exception as e:
            print(f"error :- {e}")
            
def populate_sellerPolicies(csv:bool=False):
    """
        function to populate the seller policis for each 'sku' item in database.
    """
    all_sku = fetch_oneColumn("sku")
    min_quantity =  fetch_oneColumn("minorderqty")
    pricebase = fetch_oneColumn("pricebase")

    minimum = [10,20,45]
    values = [5,8,15]
    
    dis_tiers:List[DiscountTier] = []
    
    for m,v in zip(minimum,values):
        temp = DiscountTier(minQty=m,value=v)
        dis_tiers.append(temp)
    
    dis_tiers = [dis.model_dump() for dis in dis_tiers]
    
    if csv:
        csv_df = []
    
    for sku,min_qty,pb in zip(all_sku,min_quantity,pricebase,strict=True):
        
        absoluteminprice = random.randint(max(1, int(pb * 0.5)),pb)
        
        if csv:
            df = {
                    "sku":sku,
                    "minorderqty":min_qty,
                    "absoluteminprice":absoluteminprice,
                    "discounttiers":dis_tiers
                 }
            csv_df.append(df)
            
        insert_itemPolicy(sku=sku,minorderqty=min_qty,
                          absoluteminprice=absoluteminprice,
                          discounttiers=dis_tiers)
    
    if csv:
        final_df = pd.DataFrame(csv_df)
        final_df.to_csv("sellerPolicies.csv",index=False)
        print("saved product policies to <sellerPolicies.csv>")
        

    print("Entered pollicies into db!")

### main function ###

def fake_data_gen(amt:int, csv:bool=False) -> bool:
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
        populate_sellerDatabase(amt=amt,csv=csv)
        populate_sellerPolicies(csv=csv)
        return True
    except Exception as e:
        print(f"\nFAILED")
        print(f"Exception: {type(e).__name__}")
        print(f"Message: {e}")
        raise
    