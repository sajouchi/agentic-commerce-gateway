from typing import List,Annotated
from pydantic import BaseModel, Field
import requests

from langchain_core.prompts import ChatPromptTemplate,HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage

from langchain_groq import ChatGroq

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver

from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from app.agent.node_functions import (AgentQuery_Gen, buyers_request_sim,
                                      buyers_response_to_negotiation, 
                                      call_search_api, 
                                      conditional_rounting, 
                                      counter_negotiation, 
                                      final_response, 
                                      price_guardrail, response_to_negotiation)

from app.schema.allSchema import Negotiation, filters_metadata, searchResult
from app.agent.agents import intent_retrieve_agent, negotiation_agent
from app.agent.agent_schema import queryAgent_outputSchema,queryAgent_Schema
from app.db.sellerPolicies import fetchItem_sku
from app.db.sellerDatabase import fetch_bySku

from app.db.sellerDatabase import fetch_oneColumn

from IPython.display import display,Image

from dotenv import load_dotenv
import os
load_dotenv()

### LangGraph State Graph Build ###

serde = JsonPlusSerializer(allowed_msgpack_modules=[filters_metadata])
memory = InMemorySaver(serde=serde)
thread = {"configurable":{"thread_id":"1"}}

builder = StateGraph(state_schema=queryAgent_Schema)

builder.add_node("agent_node",AgentQuery_Gen)
builder.add_node("api_call_node",call_search_api)
builder.add_node("buyers_choice_node",buyers_request_sim)

builder.add_node("agent_negotiation_node",counter_negotiation)
builder.add_node("buyers_response_node",buyers_response_to_negotiation)
builder.add_node("handle_buyers_response_node",response_to_negotiation)

builder.add_node("final_accept_reject_node",final_response)
builder.add_node("price_guardrail_node",price_guardrail)

builder.add_edge(START,"agent_node")
builder.add_edge("agent_node","api_call_node")
builder.add_edge("api_call_node","buyers_choice_node")
builder.add_edge("buyers_choice_node","price_guardrail_node")
builder.add_conditional_edges("price_guardrail_node",conditional_rounting,{
                                                                        "counter":"agent_negotiation_node",
                                                                        "accept/reject":"final_accept_reject_node"
                                                                     })
builder.add_edge("agent_negotiation_node","buyers_response_node")
builder.add_edge("buyers_response_node","handle_buyers_response_node")
builder.add_conditional_edges("handle_buyers_response_node",conditional_rounting,{
                                                                            "counter":"price_guardrail_node",
                                                                            "accept/reject":"final_accept_reject_node"
                                                                          })
builder.add_edge("final_accept_reject_node",END)
graph = builder.compile(checkpointer=memory,interrupt_before=["buyers_response_node"])

def initiate_graph(user_input:str,thread:dict) -> queryAgent_Schema:
    graph_cursor = graph.invoke({"input":user_input},
                                config=thread)
    
    return graph_cursor

def human_response(user_input:str,
                   thread:dict) -> queryAgent_Schema:
    
    graph.update_state(thread,
                       values={"buyer_response_to_negotiation":user_input})
    
    graph_cursor = graph.invoke(None,config=thread)
     
    return graph_cursor
    
### State Graph Visual Display ###

def visual_graph():
    display(Image(graph.get_graph().draw_mermaid_png()))
