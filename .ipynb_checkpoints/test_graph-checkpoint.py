from uuid import uuid4
from app.agent.agent_state_graph import (graph,visual_graph,
                                         initiate_graph,human_response)

visual_graph()

### running the graph ##

thread_id = str(uuid4())
thread = {"configurable":{"thread_id":thread_id}}

search="I want 60 Bluetooth Conference Speakers in San Francisco.Under price 5"

cur = initiate_graph(user_input=search,thread=thread)

while True:
    
    if cur.get('acceptRejectResponse') :
        print("---final Response---")
        print(cur['acceptRejectResponse'])
        break
    
    print("----negotiation response by agent---")
    print(cur['negotiationResponse'])
    user_input = input("reply?")
    cur = human_response(user_input=user_input,thread=thread)