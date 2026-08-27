import json
from app.agent.agent_state_graph import graph,visual_graph
visual_graph()

output = graph.invoke(input={"input":
         "A garmant bag of price 200. I wanna but around 89 units of it"})

# print(output['query'])
# print(output['filters'])
# print(json.dumps(output['output'],indent=4))
# print(json.dumps(output.get("negotiation_response"),indent=4))
print(output.get("accept_reject_response"))

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