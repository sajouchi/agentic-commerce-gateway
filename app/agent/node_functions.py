import requests

from app.agent.agent_schema import queryAgent_Schema, queryAgent_outputSchema
from app.db.sellerDatabase import fetch_bySku
from app.db.sellerPolicies import fetchItem_sku
from app.schema.allSchema import Negotiation, searchResult
from app.agent.agents import intent_retrieve_agent,negotiation_agent,accept_reject_agent

URL = "http://127.0.0.1:8000/api/v1/search" # Post-api url hardcoded local hosted fast api

### call search_api function ###
def call_search_api(state:dict) -> dict:
    
    query = state.query or ""
    filter_data = state.filters or ""
    
    params_args = {"query":query}
    
    # deals with empty filters dict
    filters_json_params = filter_data.model_dump() if hasattr(filter_data,"model_dump") else filter_data
    
    post_api = requests.post(url=URL,params=params_args,json=filters_json_params)
    outputs = post_api.json()
    
    formatted_output = [searchResult(**output).model_dump() for output in outputs]
    
    return {"output":formatted_output} # follows the "output"key from the queryAgent_Schema for flow in the state graph

### buyer's choice simulating function (for demo run checks) ###

def buyer_sim(state:queryAgent_Schema) -> queryAgent_Schema:
    sku = state.output[0].sku
    target_price = state.output[0].price_base - 2
    qty = state.output[0].min_order_qty+2

    return {
            "buyers_choice":{
                                "sku":sku,
                                "target_price":target_price,
                                "qty":qty
                            }
           }
### Selling Price Guardrails and Poilicies Check function ###

def price_guardrail(state:queryAgent_Schema) -> queryAgent_Schema:
    
        attempts_left = state.negotiation.retry_attempts
        
        if attempts_left <= 0:
            return {
                    "final_result":{
                                    "status":"REJECT",
                                    "reason":"retry attempts excedded the limit! "
                                   }
                   }
            
        sku = state.buyers_choice.sku or "" # hardcoded the first serached item for now! no user choice iteraction for now!
        target_price = state.buyers_choice.target_price or ""
        qty = state.buyers_choice.qty or ""
        
        item_policies = fetchItem_sku(sku=sku)
        min_order_qty = item_policies['min_order_qty']
        ### minimum order quantity rule check! ###
        if qty < min_order_qty:
            return {
                    "final_result":{
                                    "status":"REJECT",
                                    "reason":f"Quantity {qty} below minimum order quantity of {item_policies['min_order_qty']}"
                                  }
                   }
        
        discount_tiers = item_policies['discount_tiers'] # contains the items specific discount criterias
        item_data = fetch_bySku(sku=sku)
        
        item_base_price = item_data['price_base']
        applicable_discount = 0
        
        for rule in sorted(discount_tiers,key=lambda x:x['min_qty'],reverse=True):
            if qty >= rule["min_qty"]:
                applicable_discount = rule['value']
                break
        
        after_discount_price = int(item_base_price * (1-applicable_discount/100))
        
        final_item_unit_price = max(after_discount_price,item_policies['absolute_min_price'])
        guardrail_triggered = after_discount_price < item_policies['absolute_min_price']
        
        if guardrail_triggered:
            return {
                    "negotiation":{
                                    "status":"COUNTER",
                                    "counter_price":final_item_unit_price,
                                    "guardrail_triggered":guardrail_triggered,
                                    "retry_attempts":state.negotiation.retry_attempts-1,
                                    "reason":"the price of each unit can't go below absolute miniumum price!"
                                }
                    }
        if not guardrail_triggered:
            return {
                    "final_result":{
                                    "status":"ACCEPT",
                                    "final_price":final_item_unit_price,
                                    "guardrail_triggered":guardrail_triggered,
                                    "checkout_url":"https://example.com/mock/razorpay/checkout?order_id=order_test_123", # fake link for demo
                                    "expires_in":"10 minutes" # fake time for demo
                                }
                    }
    
### setting the query gen function ### 
def AgentQuery_Gen(state:queryAgent_Schema) -> queryAgent_Schema: # return updates the state_schema for the next node
    
    input = state.input or ""
    response:queryAgent_outputSchema = intent_retrieve_agent.invoke({"user_input":input})

    return {
           "query":response.query,
           "filters":response.filters
           }                        

### setting the counter negotiation node function ###

def counter_negotiation(state:queryAgent_Schema) -> queryAgent_Schema: # return updates the state_schema for the next node to work with
    
    chat_input = str(state.negotiation.model_dump_json())
    response = negotiation_agent.invoke({'user_input':chat_input})
    
    return {
            "negotiation_response":response.content or ""
           }

### setting the reject or accept with final checkout link message node function ###

def final_response(state:queryAgent_Schema) -> queryAgent_Schema:
    chat_input = str(state.final_result.model_dump_json())
    response = accept_reject_agent.invoke({"user_input":chat_input})
    
    return {
            "accept_reject_response":response.content or ""
           }
    
### conditional routing function ###

def conditional_rounting(state:queryAgent_Schema) -> str:
    negotiation = state.negotiation.status
    final_result = state.final_result.status

    print(negotiation)
    if negotiation == "COUNTER":
        return "counter"
    elif final_result == "ACCEPT":
        return "bot"
    elif final_result == "REJECT":
        return "bot"
    
    return "bot"
    