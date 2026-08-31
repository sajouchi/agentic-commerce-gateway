from app.db.sellerDatabase import fetch_bySku
from app.db.sellerPolicies import fetchItem_sku
from app.schema.agent_schema import AgentState

### Selling Price Guardrails and Poilicies Check function ###
def evaluateOffer(state:AgentState) -> AgentState:
        
        ## check for remaining retry attempts 
        
        if state.negotiation:
            attempts_left = state.negotiation[-1].retryAttempts
        else:
            attempts_left = 3
    
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
        item_data = fetch_bySku(sku=sku)
        
        if item_policies and item_data:
            
            min_order_qty = item_policies['minorderqty']
            item_base_price = item_data['pricebase']
            discount_tiers = item_policies['discounttiers'] # contains the items specific discount criterias
    
            ### minimum order quantity rule check! ###
            if qty < min_order_qty:
                return {
                        "finalResult":{
                                        "status":"REJECT",
                                        "reason":f"Quantity {qty} below minimum order quantity of {item_policies['min_order_qty']}"
                                    }
                        }    
        else:
            return {
                    "finalResult":{
                                    "status":"ERROR",
                                    "reason":"no relevent product were fetched!"
                                  }
                   }
        
        applicable_discount = 0
        
        for rule in sorted(discount_tiers,key=lambda x:x['minQty'],reverse=True):
            if qty >= rule["minQty"]:
                applicable_discount = rule['value']
                break
        
        print("------by the users search query----")
        print("targetPrice",targetPrice)
        print("qty",qty)
        print("mininum_price",item_policies['absoluteminprice'])
        print("----through vector search----")
        print("sku",sku)
        
        after_discount_price = round(item_base_price * (1-applicable_discount/100))
        
        print("---after discount Price---")
        print(after_discount_price)
        

        final_item_unit_price = max(after_discount_price,item_policies['absoluteminprice'])
        
        if targetPrice == final_item_unit_price: 
            return {
                     "finalResult":{
                                    "status":"ACCEPT",
                                    "qty":qty,
                                    "finalPrice":final_item_unit_price,
                                    "guardrailTriggered":False,
                                    "reason":"the requested price is in acceptable range.",
                                    "checkoutUrl":"https://example.com/mock/razorpay/checkout?order_id=order_test_123", # fake link for demo
                                    "expiresIn":"10 minutes" # fake time for demo
                                }
                    }
        else:
            return {
                    "negotiation":[{
                                    "status":"COUNTER",
                                    "qty":qty,
                                    "counterPrice":final_item_unit_price,
                                    "guardrailTriggered":True,
                                    "retryAttempts":attempts_left-1,
                                    "reason":"the price of each unit can't go below absolute miniumum price! the given counter price is the best discounted price."
                                }]
                    }
    