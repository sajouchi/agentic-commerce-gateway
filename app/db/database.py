from sqlmodel import create_engine

db_url = "postgresql://test3:test3@localhost:5432/commerce_db"

engine = create_engine(url=db_url,echo=True) # echo shows the sql quried running in order
