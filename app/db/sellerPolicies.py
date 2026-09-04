from typing import Any, List, Optional
from pydantic import BaseModel
from sqlmodel import JSON, Column, SQLModel, Field, Session, create_engine,text, select

from app.db.sellerDatabase import sellerDatabase
from app.schema.allSchema import discount_tier

class sellerPolicies(SQLModel,table=True):
    sku:str = Field(primary_key=True)
    absolute_min_price:int
    min_order_qty:int = Field(default=None)
    discount_tiers:List[dict[str,Any]] = Field(default=[],sa_column=Column(JSON))

# postgresql://<user>:<password>@<host>:<port>/<database_name>
db_url = "postgresql://test:test@localhost:5432/commerce_db"

engine = create_engine(url=db_url,echo=True) # echo shows the sql quried running in order

def create_db_and_table():
    SQLModel.metadata.create_all(engine)

create_db_and_table() # initialize the db and create the table 

### DB FEATURE FUNCTIONS ###

def insert_itemPolicy(sku:str,absolute_min_price:int, 
                      min_order_qty:int,discount_tiers:List[discount_tier]):
    
    """
    function to insert item policy for any item based on their 'sku' id.
    """
    
    itemPolicy = sellerPolicies(sku=sku,
                                absolute_min_price=absolute_min_price,
                                min_order_qty=min_order_qty,
                                discount_tiers=discount_tiers)
     
    with Session(engine) as session:
        try:
            session.add(itemPolicy)
            session.commit()
            
            print("committing to sellerpolicies complete")
        except Exception as e:
            session.rollback()
            print("commtting to sellerpolicies failed, error - ",e)

def fetchItem_sku(sku:str) -> dict:
    print("SKU RECEIVED:", repr(sku))
    print("SKU TYPE:", type(sku))
    with Session(engine) as session:
        statement = (select(sellerPolicies).where(sellerPolicies.sku==sku))
        print(sellerPolicies.__tablename__)
        print(engine.url)
        
        output = session.exec(statement).first()
        print(type(output.discount_tiers))
        print(output.discount_tiers)
        
        return output.model_dump() # parsed json formatted output

