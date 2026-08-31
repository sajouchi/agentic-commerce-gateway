from app.schema.agent_schema import AgentState

### condition based routing functions ###

def conditional_rounting(state:AgentState) -> str:
    
    if state.negotiation:
        negotiation = state.negotiation[-1].status

    final_result = state.finalResult.status
    buyersResponse = state.buyersResponse.response

    if final_result in ["ACCEPT","REJECT"]:
        return "accept/reject"

    if buyersResponse == "BUYERS_COUNTER_PRICE":
            return "counter"

    if buyersResponse in ["BUYER_REJECT_OFFER","BUYER_ACCEPT_COUNTER_OFFER"]:
            return "accept/reject"

    if negotiation == "COUNTER":
        return "counter"

    
    return "accept/reject"

def seach_result_routing(state:AgentState) -> AgentState:
    
    if state.finalResult.status == "REJECT":
        return "accept/reject"
    else:
        return "evaluate_offer"