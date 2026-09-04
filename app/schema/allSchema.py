import time

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

    status:Optional[Literal['COUNTER','ERROR']] = Field(default=None)
    
    qty:Optional[int] = Field(default=None)
    counterPrice:int = Field(default=None)
     
    guardrailTriggered:Optional[bool] = Field(default=None)

    reason:str = Field(default=None)
    
    retryAttempts:int = Field(default=3)
    

class FinalResult(BaseModel):
    
    finalPrice:int = Field(default=None)
    qty:Optional[int] = Field(default=None)
    status:Literal['ACCEPT','REJECT','ERROR'] = Field(default=None)
    payment_link_id:Optional[str] = Field(default=None)
    payment_id:Optional[str] = Field(default=None)
    id:Optional[str] = Field(default=None)
    reason:Optional[str] = Field(default=None)
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
                     "BUYER_ACCEPT_COUNTER_OFFER",
                     "ERROR"] = Field(default=None)
    
class DiscountTier(BaseModel):
    minQty:int = Field(default=None,description="the minimum qty required to be eligible this tier discounnt")
    discountType:str = Field(default='percentage',description="type of discount/default is %(percentage)")
    value:int = Field(default=None,description=r"the value of given discount (eg; 15% discount)")
    
class PayWebhook(BaseModel):
    razorpay_order_id:str = Field(default=None)
    razorpay_payment_id:str = Field(default=None)
    razorpay_signature:str = Field(default=None)
    
class UserDetails(BaseModel):
    name:str = Field(default=None)
    email:str = Field(default=None)
    number:int = Field(default=None)

class PaymentDetails(BaseModel):
    amount:int = Field(default=None)
    currency:str = Field(default='INR')
    description:str | None = Field(default=None)
    accept_partial: bool = Field(default=False)
    reference_id:str = Field(default=None)
    expire_by:int = Field(default=None)