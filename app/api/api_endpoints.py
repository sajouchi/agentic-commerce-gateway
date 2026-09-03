from typing import List

from fastapi import FastAPI, Request
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
        
@app.post("/razorpay/webhook")
async def weebhook(): # checks for the caputuring payment successfull or not
    data = await Request.json
    
    if not data:
        return {"status":"data not received to check capture!"}
    
    event = data['event'] # main event data sended by the razorpay webhook
    
    if event == "payment_captured":
        
        payment = data["payload"]["payment"]["entity"]

        print("🎉 PAYMENT SUCCESS")
        print("Payment ID:", payment["id"])
        print("Amount:", payment["amount"])
        
        return {"status":"payment captured!"}
    else:
        return {"status":"not captured"}
    
