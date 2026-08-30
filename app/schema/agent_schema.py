from operator import add
from typing import List, Literal, Optional, Annotated
from pydantic import BaseModel, Field

from app.schema.allSchema import (BuyersChoice, BuyersResponse, Filters, 
                                  FinalResult, SearchResult,
                                  Negotiation)

### search input/output schema ###

class AgentState(BaseModel):
    input:str = Field(default=None)
    query:str = Field(default=None)
    
    buyerResponseToNegotiation:Optional[str] = Field(default=None)
    
    filters:Filters = Field(default_factory=Filters)
    results:List[SearchResult] = []
    
    negotiation:List[Negotiation] = Annotated[List[Negotiation],add] 
    finalResult:FinalResult = Field(default_factory=FinalResult)
    
    negotiationResponse:str = Field(default=None)
    acceptRejectResponse:str = Field(default=None)
    
    buyersChoice:BuyersChoice = Field(default_factory=BuyersChoice)
    buyersResponse:BuyersResponse = Field(default_factory=BuyersResponse)
    
class QueryOutput(BaseModel):
    query:str = Field(default=None)
    filters:Filters = Field(default_factory=Filters)
