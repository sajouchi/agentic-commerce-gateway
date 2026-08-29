import json
from uuid import uuid4
from app.agent.agent_state_graph import graph,visual_graph,initiate_graph,human_response
visual_graph()

### running the graph ##

thread = {"configurable":{"thread_id":str(uuid4())}}

search="A garmant bag of price 120. I wanna but around 89 units of it"

cur = initiate_graph(user_input=search,thread=thread)
if cur['accept_reject_response']:
    print(cur['accept_reject_response'])
# print(cur['negotiation_response'])

# user_input = input("reply?")
# cur = human_response(user_input=user_input,thread=thread)

    
# input={"input":
#          "A garmant bag of price 200. I wanna but around 89 units of it"}



# for event in graph.stream(input=input,config=thread,stream_mode="values"):
#     print(event)

# print(output['query'])
# print(output['filters'])
# print(json.dumps(output['output'],indent=4))
# print(json.dumps(output.get("negotiation_response"),indent=4))
# print(output.get("accept_reject_response"))