from uuid import uuid4
from app.agent.agent_state_graph import (graph,visual_graph,
                                         initiate_graph,human_response)

visual = visual_graph()

### running the graph ##

thread_id = str(uuid4())
thread = {"configurable":{"thread_id":thread_id}}

search="I wanna buy about 60 garment bags, preferably under 9"

cur = initiate_graph(user_input=search,thread=thread)
if cur.get('acceptRejectResponse') :
    print(cur['acceptRejectResponse'])
else: 
    print(cur['negotiationResponse'])
    user_input = input("reply?")
    cur = human_response(user_input=user_input,thread=thread)
    print(cur.get("acceptRejectResponse"))
    