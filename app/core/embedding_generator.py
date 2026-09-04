from typing import Any,List

from google import genai

from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"]=os.getenv("google_api_key")

client = genai.Client()

# MAIN FUNCTIONS #

def embedContent(content:Any) -> List[int]:
    vectors = client.models.embed_content(model="gemini-embedding-001",
                                          contents=str(content))

    return vectors.embeddings[0].values

