import razorpay
import os

from dotenv import load_dotenv
load_dotenv()

from app.schema.agent_schema import AgentState
from app.schema.allSchema import PaymentDetails, UserDetails

from app.agent.agents import payLinkMessageAgent

client = razorpay.Client(auth=(f'{str(os.getenv("razor_key_id"))}',
                            f"{str(os.getenv("razor_secret_key"))}"))


def create_payment_link(state:AgentState) -> AgentState:

    details = state.finalResult
    
    payDetails = PaymentDetails(amount=(details.finalPrice * 10), # as the unit of price is * 10 (rs50 == 500),
                                description=f"payment for {details.qty} items") 
    
    pay_link = client.payment_link.create(data=payDetails)
    
    if pay_link:
        return {
                "finalPaymentURL":pay_link['short_url']
               }
    else:
        pass

# def genPaymentLinkMessage(state:AgentState) -> AgentState:
    
#     pay_link = state.finalPaymentURL
#     final_response = 
    
    