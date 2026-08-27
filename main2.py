import json
from app.agent.agent_state_graph import graph,visual_graph
visual_graph()

# from app.db.sellerPolicies import insert_itemPolicy
# insert_itemPolicy(sku='GIFT-22392',absolute_min_price=47, min_order_qty=15,discount_tiers=[{"min_qty": 10, "discount_type": "percentage", 
#                                          "value": 5}, {"min_qty": 20, "discount_type": "percentage", "value": 8}, {"min_qty": 45, "discount_type": "percentage", "value": 15}])

output = graph.invoke(input={"input":
         "A garmant bag of price 200. I wanna but around 89 units of it"})

print(output['query'])
print(output['filters'])
print(json.dumps(output['output'],indent=4))
print(json.dumps(output['negotiation'],indent=4))
print(output['chat_response'])

# from app.tools.tools import call_search_api

# response = call_search_api(query="garmant bags",filter={"price":120})
# print(response)

# import requests
# from app.schema.allSchema import filters, searchResult

# filter = {"filter":{
#                     "price":123,
#                     "qty":64
#                    }
#           }

# params_args = {"query":"electronics"}

# post_api = requests.post(url="http://127.0.0.1:8000/api/v1/search",params=params_args,json=filter)
# outputs = post_api.json()
    
# formatted_output = [searchResult(**output).model_dump() for output in outputs]

# print(formatted_output)
# out = searchResult.model_validate(formatted_output[0])
# if out:
#     print(True)
# print(type(formatted_output[0]))

# print(outputs)
# print(type(outputs))