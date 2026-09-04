from typing import Any, List, Optional

from sqlmodel import SQLModel, Field, Session, create_engine,text, select
from pgvector.sqlalchemy import VECTOR

from app.core.embedding_generator import embedContent
from app.schema.allSchema import Filters

from app.db.database import engine

VECTOR_DIMENSIONS = 3072 # google gemini-embedding-001 model output default size

class SellerDatabase(SQLModel,table=True):
    __table_args__ = {"extend_existing":True}
    
    sku:str = Field(default=None,primary_key=True)
    item:str = Field(nullable=False)
    description:str = Field(default=None)
    category:str = Field(default=None)
    company:str = Field(default=None)
    pricebase:int = Field(default=None)
    minorderqty:int = Field(default=None)
    stockquantity:int = Field(default=None)
    locationavailability:str = Field(default=None)
    vectorembeddings: list[float] = Field(sa_type=VECTOR(VECTOR_DIMENSIONS),nullable=True) # set dimension size according the model output size

# db_url = "postgresql://test3:test3@localhost:5432/commerce_db"

# engine = create_engine(url=db_url,echo=True) # echo shows the sql quried running in order

def create_db_and_table():
    SQLModel.metadata.create_all(engine)

## set vector extension before db and inside it tables creaion ##

with Session(engine) as session:
    session.exec(text("CREATE EXTENSION IF NOT EXISTS vector"))
    session.commit()

create_db_and_table() # initialize the db and create the table if not already exists

### DATABASE MAIN FUNCTIONS ###

def insertDatabase(sku:str,item:str,category:str, description:str,
                   company:str,pricebase:int,
                   minorderqty:int,stockquantity:int,
                   locationavailability:str,vectorembeddings:list[int]):
    
    new_item = SellerDatabase(sku=sku,item=item,
                              category=category,company=company, description=description,
                              pricebase=pricebase,
                              minorderqty=minorderqty,
                              stockquantity=stockquantity,
                              locationavailability=locationavailability,
                              vectorembeddings=vectorembeddings)
    
    with Session(engine) as session:
        try:
            session.add(new_item)
            session.commit()
            
            print("Committed new entry to sellerdatabase")
        except Exception as e:
            
            session.rollback()
            print("committing new try to sellerdatabase failed,error - ",e)
        

def searchByVector(query:str,filter:Filters,top_k:int=5)->List[SellerDatabase]:
    query_embedding = embedContent(content=query)
    
    with Session(engine) as session:
        statement = select(SellerDatabase)

        filter_runs = []

        if filter.price is not None:
            filter_runs.append(SellerDatabase.pricebase <= filter.price)
        if filter.qty is not None:
            filter_runs.append(SellerDatabase.minorderqty <= filter.qty)
        if filter.brand is not None:
            filter_runs.append(SellerDatabase.company == filter.brand)
        
        if filter_runs:
            statement = statement.where(*filter_runs)

        statement = statement.order_by(SellerDatabase.vectorembeddings.\
                cosine_distance(query_embedding)).limit(top_k)
        
        top_k_output = session.exec(statement).all()
        return top_k_output

def simpleVector_search(query:str,top_k:int=5)->List[SellerDatabase]:
    query_embedding = embedContent(content=query)
    
    with Session(engine) as session:
        statement = (select(SellerDatabase).order_by(SellerDatabase.vectorembeddings.\
            cosine_distance(query_embedding)).limit(top_k))
        
        top_k_output = session.exec(statement).all()
        return top_k_output

def simple_fetchAll() -> List[Any]:
    
    with Session(engine) as session:
        statement = (select(SellerDatabase))
        output = session.exec(statement).all()
        
        return output

def fetch_bySku(sku:str) -> SellerDatabase | dict:

    # raw_query = text("""SELECT sku,item,description,category,
    #            company,pricebase,minorderqty,
    #            stockquantity,locationavailability FROM sellerdatabase WHERE sku LIKE :sku""") # raw filter columns query
    
    with Session(engine) as session:
        statement = select(SellerDatabase).where(SellerDatabase.sku==sku) # sqlmodel approach
        output = session.exec(statement).first()
        
        if output:
            return output.model_dump()
        else:
            None

def fetch_oneColumn(column:str) -> List[str]:
    
    selected_column = getattr(SellerDatabase,column)
    
    with Session(engine) as session:
        
        statement = (select(selected_column))
        output = session.exec(statement).all()
        
        return output       