from typing import Any, List, Optional
from pydantic import BaseModel
from sqlmodel import JSON, Column, SQLModel, Field, Session, create_engine, select

from app.schema.allSchema import DiscountTier

class SellerPolicies(SQLModel,table=True):
    sku:str = Field(primary_key=True)
    absoluteminprice:int
    minorderqty:int = Field(default=None)
    discounttiers:List[dict[str,Any]] = Field(default=[],sa_column=Column(JSON))

# postgresql://<user>:<password>@<host>:<port>/<database_name>
db_url = "postgresql://test3:test3@localhost:5432/commerce_db"

engine = create_engine(url=db_url,echo=True) # echo shows the sql quried running in order

def create_db_and_table():
    SQLModel.metadata.create_all(engine)

create_db_and_table() # initialize the db and create the table 

### DB FEATURE FUNCTIONS ###

def insert_itemPolicy(sku:str,absoluteminprice:int, 
                      minorderqty:int,discounttiers:List[DiscountTier]):
    
    """
    function to insert item policy for any item based on their 'sku' id.
    """
    
    itemPolicy = SellerPolicies(sku=sku,
                                absoluteminprice=absoluteminprice,
                                minorderqty=minorderqty,
                                discounttiers=discounttiers)
     
    with Session(engine) as session:
        session.add(itemPolicy)
        session.commit()

def fetchItem_sku(sku:str) -> dict:
    print("SKU RECEIVED:", repr(sku))
    print("SKU TYPE:", type(sku))
    with Session(engine) as session:
        statement = (select(SellerPolicies).where(SellerPolicies.sku==sku))
        print(SellerPolicies.__tablename__)
        print(engine.url)
        
        output = session.exec(statement).first()
        print(type(output.discounttiers))
        print(output.discounttiers)
        
        return output.model_dump() # parsed json formatted output

