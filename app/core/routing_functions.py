from app.db.sellerPayments import fetch_paymentStatusByLinkID
from app.schema.agent_schema import AgentState

### condition based routing functions ###

def conditional_rounting(state:AgentState) -> str:
    
    if state.negotiation:
        negotiation = state.negotiation[-1].status

    final_result = state.finalResult.status
    buyersResponse = state.buyersResponse.response

    if final_result in ["REJECT","ERROR"]:
        return "accept/reject"
    
    if final_result == 'ACCEPT':
        return "payment"

    if buyersResponse == "BUYERS_COUNTER_PRICE":
            return "counter"

    if buyersResponse == "BUYER_REJECT_OFFER":
            return "accept/reject"
        
    if buyersResponse == "BUYER_ACCEPT_COUNTER_OFFER":
        return "payment"

    if negotiation == "COUNTER":
        return "counter"

    return "accept/reject"

def seach_result_routing(state:AgentState) -> str:
    
    if state.finalResult.status == "REJECT":
        return "accept/reject"
    else:
        return "evaluate_offer"

def payment_route(state:AgentState) -> str:
        
    id = state.finalResult.payment_link_idy
    if fetch_paymentStatusByLinkID(id=id) == "paid":
        return "success"
    else:
        return "failure"