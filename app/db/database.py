from sqlmodel import create_engine
import os

from dotenv import load_dotenv
load_dotenv()

# db_url_local = "postgresql://test3:test3@localhost:5432/commerce_db"

db_url_managed = os.getenv("neon_db_url")

engine = create_engine(url=db_url_managed,echo=True) # echo shows the sql quried running in order
