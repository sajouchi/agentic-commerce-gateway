from pydantic import BaseModel, Field
from typing import Optional, Literal, Any

class searchBase(BaseModel):
    query:str

class searchResult(BaseModel):
    sku:str
    item:str
    description:str
    price_base:int
    min_order_qty:int

class filters_metadata(BaseModel):
    price:Optional[int] = Field(default=None)
    qty:Optional[int] = Field(default=None)
    brand:Optional[str] = Field(default=None)

class Negotiation(BaseModel):
    sku:Optional[str] = Field(default=None)
    buyer_price:Optional[int] = Field(default=None)
    qty:Optional[int] = Field(default=None)
    
    status:Literal['ACCEPT','REJECT','COUNTER'] = Field(default=None)
    counter_price:int = Field(default=None) 
    final_price:int = Field(default=None)
    reason:str = Field(default=None)
    
    retry_attempts:int = Field(default=3)
    
    checkout_url:str = Field(default=None)
    expires_in:str = Field(default=None)
    
class buyersChoice_schema(BaseModel):
    sku:str = Field(default=None)
    target_price:int = Field(default=None)
    qty:int = Field(default=None)
    
class discount_tier(BaseModel):
    min_qty:int = Field(default=None,description="the minimum qty required to be eligible this tier discounnt")
    discount_type:str = Field(default='percentage',description="type of discount/default is %(percentage)")
    value:int = Field(default=None,description=r"the value of given discount (eg; 15% discount)")
    