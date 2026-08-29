import requests

from app.agent.agent_schema import AgentState, QueryOutput
from app.db.sellerDatabase import fetch_bySku
from app.db.sellerPolicies import fetchItem_sku
from app.schema.allSchema import BuyersResponse, SearchResult
from app.agent.agents import (intentAgent,counterOfferAgent,
                              finalResponseAgent, buyerResponseAgent)

URL = "http://127.0.0.1:8000/api/v1/search" # Post-api url hardcoded local hosted fast api

### call search_api function ###
def searchApi(state:AgentState) -> AgentState:
    
    query = state.query or ""
    filter_data = state.filters or ""
    
    params_args = {"query":query}
    
    # deals with empty filters dict
    filters_json_params = filter_data.model_dump() if hasattr(filter_data,"model_dump") else filter_data
    
    post_api = requests.post(url=URL,params=params_args,json=filters_json_params)
    outputs = post_api.json()
    
    formatted_output = [SearchResult(**output).model_dump() for output in outputs]
    
    return {"results":formatted_output} # follows the "output"key from the AgentState for flow in the state graph

### buyer's choice simulating function (for demo run checks) ###

def prepareBuyersRequest(state:AgentState) -> AgentState:
    sku = state.results[0].sku # obtained by the queried vector search result from db
    
    # by the search query from the buyer
    # targetPrice = 57 # just for demo to test COUNTER node
    targetPrice = state.filters.price 
    qty = state.filters.qty

    return {
            "buyersChoice":{
                                "sku":sku,
                                "targetPrice":targetPrice,
                                "qty":qty
                            }
           }
### Selling Price Guardrails and Poilicies Check function ###

def evaluateOffer(state:AgentState) -> AgentState:
        
        ## check for remaining retry attempts 
        attempts_left = state.negotiation.retryAttempts
    
        if attempts_left <= 0:
            return {
                    "finalResult":{
                                    "status":"REJECT",
                                    "reason":"retry attempts excedded the limit! "
                                   }
                   }
            
        sku = state.buyersChoice.sku or "" # hardcoded the first serached item for now! no user choice iteraction for now!
        
        if state.buyersResponse.response == "BUYERS_COUNTER_PRICE":
            targetPrice = state.buyersResponse.buyersCounterPrice or None
            qty = state.buyersResponse.qty or None
        else:
            targetPrice = state.buyersChoice.targetPrice or None
            qty = state.buyersChoice.qty or None
        
        item_policies = fetchItem_sku(sku=sku)
        min_order_qty = item_policies['minOrderQty']
        ### minimum order quantity rule check! ###
        if qty < min_order_qty:
            return {
                    "finalResult":{
                                    "status":"REJECT",
                                    "reason":f"Quantity {qty} below minimum order quantity of {item_policies['min_order_qty']}"
                                  }
                   }
        
        discount_tiers = item_policies['discountTiers'] # contains the items specific discount criterias
        item_data = fetch_bySku(sku=sku)
        
        item_base_price = item_data['priceBase']
        applicable_discount = 0
        
        for rule in sorted(discount_tiers,key=lambda x:x['minQty'],reverse=True):
            if qty >= rule["minQty"]:
                applicable_discount = rule['value']
                break
        
        print("------by the users search query----")
        print("targetPrice",targetPrice)
        print("qty",qty)
        print("----through vector search----")
        print("sku",sku)
        
        after_discount_price = int(item_base_price * (1-applicable_discount/100))
        
        print("---after discount Price---")
        print(after_discount_price)
        
        if targetPrice >= after_discount_price and targetPrice >= item_policies['absolute_min_price']:
            final_item_unit_price = targetPrice
            guardrail_triggered = False
        else:
            final_item_unit_price = max(after_discount_price,item_policies['absolute_min_price'])
            guardrail_triggered = True
        
        if guardrail_triggered: 
            return {
                    "negotiation":{
                                    "status":"COUNTER",
                                    "qty":qty,
                                    "counterPrice":final_item_unit_price,
                                    "guardrailTriggered":guardrail_triggered,
                                    "retryAttempts":state.negotiation.retryAttempts-1,
                                    "reason":"the price of each unit can't go below absolute miniumum price! the given counter price is the best discounted price."
                                }
                    }
        if not guardrail_triggered:
            return {
                    "finalResult":{
                                    "status":"ACCEPT",
                                    "qty":qty,
                                    "finalPrice":final_item_unit_price,
                                    "guardrailTriggered":guardrail_triggered,
                                    "checkoutUrl":"https://example.com/mock/razorpay/checkout?order_id=order_test_123", # fake link for demo
                                    "expiresIn":"10 minutes" # fake time for demo
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
    
    chat_input = str(state.negotiation.model_dump_json())
    response = counterOfferAgent.invoke({'user_input':chat_input})
    
    return {
            "negotiationResponse":response.content or ""
           }

## setting the buyers negotiation offers response handle node function ###

def classifyBuyerResponse(state:AgentState) -> AgentState:
    
    chat_input = str(state.buyerResponseToNegotiation)
    print(chat_input)
    
    response:BuyersResponse = buyerResponseAgent.invoke({"user_input":chat_input})
    
    return {
            "buyersResponse":{
                                "targetPrice":response.buyersCounterPrice or None,
                                "qty":response.qty or None,
                                "response":response.response or None
                              }
           }

### setup the response by the buyer for the negotiation ###

def resolveBuyerResponse(state:AgentState) -> AgentState:
    
    final_price = state.negotiation.counterPrice or None
    qty = state.buyersResponse.qty or state.negotiation.qty
    
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
        
        elif state.buyersResponse.response is None:
            status = None
            return {
                     "finalResult":{
                                        "status":status,
                                        "reason":"got incomprehensible responseor no response received, which resulted in rejection."
                                    }        
                   }
        
        elif state.buyersResponse.response == "BUYER_ACCEPT_COUNTER_OFFER":
            status = "ACCEPT"
        
            return {
                    "finalResult":{
                                    "final_price":final_price or "",
                                    "qty":qty,
                                    "status" : status,
                                    "checkoutUrl":"https://example.com/mock/razorpay/checkout?order_id=order_test_123", # fake link for demo
                                    "expiresIn":"10 minutes" # fake time for demo
                                    }
                                }
        

### setting the reject or accept with final checkout link message node function ###

def generateFinalResponse(state:AgentState) -> AgentState:
    chat_input = str(state.finalResult.model_dump_json())
    response = finalResponseAgent.invoke({"user_input":chat_input})
    
    return {
            "acceptRejectResponse":response.content or None
           }
    
### conditional routing function ###

def conditional_rounting(state:AgentState) -> str:
    negotiation = state.negotiation.status
    final_result = state.finalResult.status
    buyersResponse = state.buyersResponse.response

    if final_result in ["ACCEPT","REJECT"]:
        return "accept/reject"

    if buyersResponse == "BUYERS_COUNTER_PRICE":
            return "counter"

    if buyersResponse in ["BUYER_REJECT_OFFER","BUYER_ACCEPT_COUNTER_OFFER"]:
            return "accept/reject"

    if negotiation == "COUNTER":
        return "counter"
    
    return "accept/reject"
    