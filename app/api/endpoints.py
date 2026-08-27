from typing import List

from fastapi import FastAPI
from app.schema.allSchema import searchBase, searchResult,filters_metadata

from app.db.sellerDatabase import searchByVector
import asyncio

app = FastAPI(root_path="/api/v1",
              version='0.1')

@app.get("/")
async def Live():
    return { "status":"Live!"}

@app.post("/search",response_model=List[searchResult])
async def search(query:str,filter:filters_metadata):
    outputs = searchByVector(query=query,filter=filter, top_k=5)

    final_output = [searchResult(sku=output.sku,
                                    item=output.item,
                                    description=output.description,
                                    price_base=output.price_base,
                                    min_order_qty=output.min_order_qty) for output in outputs]

    return final_output

