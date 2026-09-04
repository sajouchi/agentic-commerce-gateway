import razorpay
import os

from dotenv import load_dotenv
load_dotenv()

from app.db.sellerPayments import create_payment_record
from app.schema.agent_schema import AgentState
from app.schema.allSchema import PaymentDetails, UserDetails
import time

from app.agent.agents import finalResponseAgent

client = razorpay.Client(auth=(f'{str(os.getenv("razor_key_id"))}',
                            f"{str(os.getenv("razor_secret_key"))}"))


def create_payment_link(state:AgentState) -> AgentState:

    details = state.finalResult
    
    payDetails = PaymentDetails(amount=(details.finalPrice * 10 * 10), # as the unit of price is * 10 (rs50 == 500),
                                description=f"payment for {details.qty} items",
                                expire_by=int(time.time())+20*60)  # 15-20 minutes expiry limit
    
    pay_link = client.payment_link.create(data=payDetails.model_dump(exclude_none=True))
    
    print("----Payment Link ID----")
    print(pay_link['id'])
    
    create_payment_record(payment_link_id=pay_link['id'],
                          amount=details.finalPrice) # initial record make
    
    if pay_link:
        
        return {
                "finalResult":{**state.finalResult.model_dump(),
                               "checkoutUrl":pay_link['short_url'], # fake links generated for demo test razorpay api
                              "payment_link_id":pay_link['id'],
                              "expiresIn":"15 minutes"}
               }
    else:
        pass

