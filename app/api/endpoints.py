from typing import List

from fastapi import FastAPI
from app.schema.allSchema import SearchQuery, SearchResult,Filters

from app.db.sellerDatabase import searchByVector
import asyncio

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
                                    priceBase=output.priceBase,
                                    minOrderQty=output.minOrderQty) for output in outputs]

    return final_output

# @app.post("/feedback",)
