from typing import List

from fastapi import FastAPI, Request
from app.db.sellerPayments import update_payment_status
from app.schema.allSchema import (SearchQuery, SearchResult,
                                  Filters, PayWebhook)

from app.db.sellerDatabase import searchByVector
import razorpay
import asyncio

from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI(root_path="/api/v1",
              version='0.1')

@app.get("/")
async def Live():
    return { "status":"Live!"}

@app.post("/search",response_model=List[SearchResult])
async def search(query:str,filter:Filters):
    outputs = searchByVector(query=query,filter=filter, top_k=5)

    final_output = [SearchResult(sku=output.sku,
                                    item=output.item,
                                    description=output.description,
                                    priceBase=output.pricebase,
                                    minOrderQty=output.minorderqty) for output in outputs]

    return final_output

@app.post("/user_response") # for the human respose part
async def user_response(response:str):
    return {
            "user_response":response
           }

@app.post("/razorpay/veryify")
async def verify(pay_signature:PayWebhook):
    client = razorpay.Client(auth=(f'{str(os.getenv("razor_key_id"))}',
                                   f"{str(os.getenv("razor_secret_key"))}"))
    
    try:
        client.utility.verify_payment_signature(pay_signature.model_dump())
        return True
    except razorpay.errors.SignatureVerificationError:
        raise "Invalid Payment Attempt"
    
### weebhoook to configure on the razorpay for payment capture ###
@app.post("/razorpay/webhook")
async def weebhook(request:Request): # checks for the caputuring payment successfull or not
    data = await request.json()
    
    event = data['event'] # main event data sended by the razorpay webhook
    
    # print(data)
    
    if event == "payment_link.paid":

        payment_info = data["payload"]["payment"]["entity"]
        payment_link_id= data["payload"]["payment_link"]["entity"]["id"]

        print("---PAYMENT PAID CAPTURE SUCCESS---")
        print("payment_id:", payment_info["id"])
        print("amount:", payment_info["amount"])
        print("payment_link_id:",payment_link_id)
        
        update_payment_status(payment_link_id=payment_link_id,
                              payment_id=str(payment_info['id']),
                           status="paid")  

    return {"status":"ok"}
