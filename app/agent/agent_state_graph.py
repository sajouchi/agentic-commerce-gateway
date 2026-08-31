from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from app.core.prep_and_response import (SearchQueryGen,prepareBuyersRequest, 
                                        resolveBuyerResponse,
                                       classifyBuyerResponse, 
                                       counterResponseGen, 
                                       generateFinalResponse)

from app.core.api_call_function import searchApi
from app.core.evalute_offers import evaluateOffer
from app.core.routing_functions import conditional_rounting, seach_result_routing

from app.schema.allSchema import Filters
from app.schema.agent_schema import AgentState

from IPython.display import display,Image

### LangGraph State Graph Build ###
serde = JsonPlusSerializer(allowed_msgpack_modules=[Filters]) # config to avoid warning about not default custom schemas

memory = InMemorySaver(serde=serde)
thread = {"configurable":{"thread_id":"1"}}

builder = StateGraph(state_schema=AgentState)

builder.add_node("agent_node",SearchQueryGen)
builder.add_node("api_call_node",searchApi)

builder.add_node("buyers_choice_node",prepareBuyersRequest)

builder.add_node("agent_negotiation_node",counterResponseGen)
builder.add_node("buyers_response_node",classifyBuyerResponse)
builder.add_node("handle_buyers_response_node",resolveBuyerResponse)

builder.add_node("final_accept_reject_node",generateFinalResponse)
builder.add_node("evaluate_offer_node",evaluateOffer)

builder.add_edge(START,"agent_node")
builder.add_edge("agent_node","api_call_node")
builder.add_edge("api_call_node","buyers_choice_node")
builder.add_conditional_edges("buyers_choice_node",seach_result_routing,{
                                                                          "accept/reject":"final_accept_reject_node",
                                                                          "evaluate_offer":"evaluate_offer_node"
                                                                        })
builder.add_conditional_edges("evaluate_offer_node",conditional_rounting,{
                                                                        "counter":"agent_negotiation_node",
                                                                        "accept/reject":"final_accept_reject_node"
                                                                     })
builder.add_edge("agent_negotiation_node","buyers_response_node")
builder.add_edge("buyers_response_node","handle_buyers_response_node")
builder.add_conditional_edges("handle_buyers_response_node",conditional_rounting,{
                                                                            "counter":"evaluate_offer_node",
                                                                            "accept/reject":"final_accept_reject_node"
                                                                          })
builder.add_edge("final_accept_reject_node",END)
graph = builder.compile(checkpointer=memory,interrupt_before=["buyers_response_node"])


### functions to test out graph and its working ###

def initiate_graph(user_input:str,thread:dict) -> AgentState:
    graph_cursor = graph.invoke({"input":user_input},
                                config=thread)
    
    return graph_cursor

def human_response(user_input:str,
                   thread:dict) -> AgentState:
    
    graph.update_state(thread,
                       values={"buyerResponseToNegotiation":user_input})
    
    graph_cursor = graph.invoke(None,config=thread)
     
    return graph_cursor
    
### State Graph Visual Display ###

def visual_graph():
    display(Image(graph.get_graph().draw_mermaid_png()))
