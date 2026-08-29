from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from app.schema.allSchema import buyersResponse, filters_metadata, finalize, searchResult, Negotiation, buyersChoice_schema

### search input/output schema ###

class queryAgent_Schema(BaseModel):
    input:str = Field(default=None)
    query:str = Field(default=None)
    
    buyer_response_to_neogtiation:Optional[str] = Field(default=None)
    
    filters:filters_metadata = Field(default_factory=filters_metadata)
    output:List[searchResult] = []
    
    negotiation:Negotiation = Field(default_factory=Negotiation)
    final_result:finalize = Field(default_factory=finalize)
    
    negotiation_response:str = Field(default=None)
    accept_reject_response:str = Field(default=None)
    
    buyers_choice:buyersChoice_schema = Field(default_factory=buyersChoice_schema)
    buyers_response:buyersResponse = Field(default_factory=buyersResponse)
    
class queryAgent_outputSchema(BaseModel):
    query:str = Field(default=None)
    filters:filters_metadata = Field(default_factory=filters_metadata)
    
class negotiationAgent_outputSchema(BaseModel):
    status:Literal['ACCEPT','REJECT','COUNTER'] = Field(default=None)
    counter_price:int = Field(default=None) 
    final_price:int = Field(default=None)
    reason:str = Field(default=None)
    retry_attempts:int = Field(default=3)
    checkout_url:str = Field(default=None)
    expires_in:str = Field(default=None)
    