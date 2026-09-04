from fastapi import HTTPException, status
import requests

from app.schema.agent_schema import AgentState
from app.schema.allSchema import SearchResult

import os
from dotenv import load_dotenv
load_dotenv()

URL = str(os.getenv("search_api_endpoint")) # Post-api url hardcoded local hosted fast api

### call search_api function ###
def searchApi(state:AgentState) -> AgentState:
    
    query = state.query or ""
    filter_data = state.filters or ""
    
    params_args = {"query":query}
    
    # deals with empty filters dict
    filters_json_params = filter_data.model_dump() if hasattr(filter_data,"model_dump") else filter_data
    
    # calling post api with error handling
    try:
        post_api = requests.post(url=URL,params=params_args,json=filters_json_params)
        post_api.raise_for_status()
        outputs = post_api.json()
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                            detail="external api timed out")
        
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else 502
        raise HTTPException(status_code = status_code,
                            detail=f"External api error :- {str(e)}")
        
    except requests.exceptions.InvalidJSONError as e:
        raise HTTPException(status_code=e.response.status_code,
                            detail=f"invalid json passed error {str(e)}")
    
    formatted_output = [SearchResult(**output).model_dump() for output in outputs]
    
    return {"results":formatted_output} # follows the "output"key from the AgentState for flow in the state graph
