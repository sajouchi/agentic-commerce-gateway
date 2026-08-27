import json
from app.agent.agent_state_graph import graph,visual_graph
visual_graph()

### running the graph ##
input={"input":
         "A garmant bag of price 200. I wanna but around 89 units of it"}

thread = {"cofigurable":{"thread_id":"1"}}

for event in graph.stream(input=input,config=thread,stream_mode="values"):
    print(event)

# print(output['query'])
# print(output['filters'])
# print(json.dumps(output['output'],indent=4))
# print(json.dumps(output.get("negotiation_response"),indent=4))
# print(output.get("accept_reject_response"))