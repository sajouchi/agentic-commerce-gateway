from pydantic import BaseModel, Field
from typing import Optional, Literal, Any

class SearchQuery(BaseModel):
    query:str

class SearchResult(BaseModel):
    sku:str | None
    item:str | None
    description:str | None
    priceBase:int | None
    minOrderQty:int | None

class Filters(BaseModel):
    price:int | None = Field(default=None)
    qty:int | None = Field(default=None)
    brand:Optional[str] = Field(default=None)

class Negotiation(BaseModel):

    status:Optional[Literal['COUNTER']] = Field(default=None)
    
    qty:Optional[int] = Field(default=None)
    counterPrice:int = Field(default=None)
     
    guardrailTriggered:Optional[bool] = Field(default=None)

    reason:str = Field(default=None)
    
    retryAttempts:int = Field(default=3)
    

class FinalResult(BaseModel):
    
    finalPrice:int = Field(default=None)
    qty:Optional[int] = Field(default=None)
    status:Literal['ACCEPT','REJECT'] = Field(default=None)
    reason:str = Field(default=None)
    checkoutUrl:str = Field(default=None)
    expiresIn:str = Field(default=None)
    
class BuyersChoice(BaseModel):
    sku:Optional[str] = Field(default=None) # just for demo, prod will not have sku as user won't provide that
    targetPrice:Optional[int] = Field(default=None)
    qty:Optional[int] = Field(default=None)
    brand:Optional[str]  = Field(default=None)
    
class BuyersResponse(BaseModel):
    buyersCounterPrice:Optional[int] = Field(default=None)
    qty:Optional[int] = Field(default=None)
    response:Literal['BUYERS_COUNTER_PRICE',
                     "BUYER_REJECT_OFFER",
                     "BUYER_ACCEPT_COUNTER_OFFER"] = Field(default=None)
    
class DiscountTier(BaseModel):
    minQty:int = Field(default=None,description="the minimum qty required to be eligible this tier discounnt")
    discountType:str = Field(default='percentage',description="type of discount/default is %(percentage)")
    value:int = Field(default=None,description=r"the value of given discount (eg; 15% discount)")
    