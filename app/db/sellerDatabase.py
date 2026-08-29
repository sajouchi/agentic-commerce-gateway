from typing import Any, List, Optional

from sqlmodel import SQLModel, Field, Session, create_engine,text, select
from pgvector.sqlalchemy import VECTOR

from app.core.embeddingFunctions import embedContent
from app.schema.allSchema import filters_metadata

VECTOR_DIMENSIONS = 3072 # google gemini-embedding-001 model output default size

class sellerDatabase(SQLModel,table=True):
    sku:str = Field(default=None,primary_key=True)
    item:str = Field(nullable=False)
    description:str = Field(default=None)
    category:str = Field(default=None)
    company:str = Field(default=None)
    price_base:int = Field(default=None)
    min_order_qty:int = Field(default=None)
    stock_quantity:int = Field(default=None)
    location_availability:str = Field(default=None)
    vector_embedding: list[float] = Field(sa_type=VECTOR(VECTOR_DIMENSIONS),nullable=True) # set dimension size according the model output size

db_url = "postgresql://test3:test3@localhost:5432/commerce_db"

engine = create_engine(url=db_url,echo=True) # echo shows the sql quried running in order

def create_db_and_table():
    SQLModel.metadata.create_all(engine)

## set vector extension before db and inside it tables creaion ##

with Session(engine) as session:
    session.exec(text("CREATE EXTENSION IF NOT EXISTS vector"))
    session.commit()

create_db_and_table() 

### DATABASE MAIN FUNCTIONS ###

def insertDatabase(sku:str,item:str,category:str, description:str,
                   company:str,price_base:int,
                   min_order_qty:int,stock_quantity:int,
                   location_availability:str,vector_embedding:list[int]):
    
    new_item = sellerDatabase(sku=sku,item=item,
                              category=category,company=company, description=description,
                              price_base=price_base,
                              min_order_qty=min_order_qty,
                              stock_quantity=stock_quantity,
                              location_availability=location_availability,
                              vector_embedding=vector_embedding)
    
    with Session(engine) as session:
        try:
            session.add(new_item)
            session.commit()
        except Exception as e:
            session.rollback()
            print("error:-",e)
        

def searchByVector(query:str,filter:filters_metadata,top_k:int=5)->List[sellerDatabase]:
    query_embedding = embedContent(content=query)
    
    with Session(engine) as session:
        statement = select(sellerDatabase)

        filter_runs = []

        if filter.price is not None:
            filter_runs.append(sellerDatabase.price_base <= filter.price)
        if filter.qty is not None:
            filter_runs.append(sellerDatabase.min_order_qty <= filter.qty)
        if filter.brand is not None:
            filter_runs.append(sellerDatabase.company == filter.brand)
        
        if filter_runs:
            statement = statement.where(*filter_runs)

        statement = statement.order_by(sellerDatabase.vector_embedding.\
                cosine_distance(query_embedding)).limit(top_k)
        
        top_k_output = session.exec(statement).all()
        return top_k_output

def simpleVector_search(query:str,top_k:int=5)->List[sellerDatabase]:
    query_embedding = embedContent(content=query)
    
    with Session(engine) as session:
        statement = (select(sellerDatabase).order_by(sellerDatabase.vector_embedding.\
            cosine_distance(query_embedding)).limit(top_k))
        
        top_k_output = session.exec(statement).all()
        return top_k_output

def simple_fetchAll() -> List[Any]:
    
    with Session(engine) as session:
        statement = (select(sellerDatabase))
        output = session.exec(statement).all()
        
        return output

def fetch_bySku(sku:str) -> sellerDatabase | dict:

    # raw_query = text("""SELECT sku,item,description,category,
    #            company,price_base,min_order_qty,
    #            stock_quantity,location_availability FROM sellerdatabase WHERE sku LIKE :sku""") # raw filter columns query
    
    with Session(engine) as session:
        statement = select(sellerDatabase).where(sellerDatabase.sku==sku) # sqlmodel approach
        output = session.exec(statement).first()
        
        return output.model_dump()

def fetch_oneColumn(column:str) -> List[str]:
    
    selected_column = getattr(sellerDatabase,column)
    
    with Session(engine) as session:
        
        statement = (select(selected_column))
        output = session.exec(statement).all()
        
        return output       