from langchain_core.tools import tool
from app.schema.allSchema import filters,searchResult

import requests
from typing import List

URL = "http://127.0.0.1:8000/api/v1/search" # hardcoded post api url for now

