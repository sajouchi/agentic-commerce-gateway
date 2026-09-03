from app.schema.agent_schema import AgentState, QueryOutput
from app.schema.allSchema import BuyersResponse
from app.agent.agents import (intentAgent,counterOfferAgent,
                              finalResponseAgent, buyerResponseAgent)

### buyer's request structurizing function ###

def prepareBuyersRequest(state:AgentState) -> AgentState:
    
    if len(state.results) == 0:
        return {
                    "finalResult":{
                                    "status":"ERROR",
                                    "reason":"no matching products were found for requested criterias."
                                  }
               }
    
    sku = state.results[0].sku # obtained by the queried vector search result from db
    
    # by the search query from the buyer
    # targetPrice = 57 # just for demo to test COUNTER node
    if state.filters:
        targetPrice = state.filters.price or None
        qty = state.filters.qty or None
        brand = state.filters.brand or ""
    else:
        targetPrice=None
        qty=None
        brand=None
        

    return {
            "buyersChoice":{
                                "sku":sku,
                                "targetPrice":targetPrice,
                                "qty":qty,
                                "brand":brand
                            }
           }

### setting the query gen function ### 
def SearchQueryGen(state:AgentState) -> AgentState: # return updates the state_schema for the next node
    
    input = state.input or ""
    response:QueryOutput = intentAgent.invoke({"user_input":input})

    return {
           "query":response.query,
           "filters":response.filters
           }                        

### setting the counter negotiation node function ###

def counterResponseGen(state:AgentState) -> AgentState: # return updates the state_schema for the next node to work with
    
    print("----counter json load---")
    print(state.negotiation[-1].model_dump_json())
    
    chat_input = state.negotiation[-1].model_dump_json()
    response = counterOfferAgent.invoke({'user_input':chat_input})
    
    print("----negotiation response by agent----")
    print(response.content)
    
    return {
            "negotiationResponse":response.content or ""
           }

## setting the buyers negotiation offers response handle node function ###

def classifyBuyerResponse(state:AgentState) -> AgentState:
    
    print("----buyers response to negotiation-----")
    print(state.buyerResponseToNegotiation)
    
    chat_input = str(state.buyerResponseToNegotiation)
    print(chat_input)
    
    response:BuyersResponse = buyerResponseAgent.invoke({"user_input":chat_input})
    print("----classify buyers response result-----")
    print(response)
    
    return {
            "buyersResponse":{
                                "buyersCounterPrice":response.buyersCounterPrice or None,
                                "qty":response.qty or None,
                                "response":response.response or None
                              }
           }

### setup the response by the buyer for the negotiation ###

def resolveBuyerResponse(state:AgentState) -> AgentState:
    
    if state.negotiation:
        final_price = state.negotiation[-1].counterPrice or None
        qty = state.buyersResponse.qty or state.negotiation[-1].qty
    else:
        final_price=None
        qty = state.buyersResponse.qty
    
    print("BUYER RESPONSE:", repr(state.buyersResponse.response))
    
    if state.buyersResponse.response == "BUYERS_COUNTER_PRICE":
        return {}
    else:
        
        if state.buyersResponse.response == "BUYER_REJECT_OFFER":
            status = "REJECT"
            return {
                     "finalResult":{
                                        "status":status,
                                        "reason":"rejected the counter offer"
                                    }        
                   }
        
        elif state.buyersResponse.response == "ERROR" or None:
            status = "ERROR"
            return {
                     "finalResult":{
                                        "status":status,
                                        "reason":"got incomprehensible response or no response received, which resulted in system process error"
                                    }        
                   }
        
        elif state.buyersResponse.response == "BUYER_ACCEPT_COUNTER_OFFER":
            status = "ACCEPT"
        
            return {
                    "finalResult":{
                                    "finalPrice":final_price or "",
                                    "qty":qty,
                                    "status" : status,
                                    "checkoutUrl":"https://example.com/mock/razorpay/checkout?order_id=order_test_123", # fake link for demo
                                    "expiresIn":"10 minutes" # fake time for demo
                                    }
                                }
        

### setting the reject or accept with final checkout link message node function ###

def generateFinalResponse(state:AgentState) -> AgentState:
    
    print("\n========== FINAL RESULT OBJECT ==========")
    print(state.finalResult)
    print("\n========== FINAL RESULT JSON ==========")
    print(state.finalResult.model_dump_json())
    print("\n========== STATUS ==========")
    print(repr(state.finalResult.status))
    print("\n========== FINAL PRICE ==========")
    print(repr(state.finalResult.finalPrice))
    print("\n========== QTY ==========")
    print(repr(state.finalResult.qty))
    print("=========================================")
    
    chat_input = state.finalResult.model_dump_json()
    response = finalResponseAgent.invoke({"user_input":chat_input})
    print(repr(response.content))
    
    return {    
            "acceptRejectResponse":response.content or None
           }
    
