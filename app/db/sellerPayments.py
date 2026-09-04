from typing import Any, List, Optional

from sqlmodel import SQLModel, Field, Session, create_engine,text, select
from app.db.database import engine

print("SELLER PAYMENTS LOADED:", __name__)
print("MODULE:", __file__)

class buyer(SQLModel,table=True):
    __table_args__ = {"extend_existing":True}
    
    payment_link_id:str = Field(primary_key=True,nullable=False)
    payment_id:Optional[str] = Field(default=None,nullable=True)
    amount:Optional[int] = Field(default=None,nullable=True)
    status:Optional[str] = Field(default=None,nullable=True)

# db_url = "postgresql://test3:test3@localhost:5432/commerce_db"

# engine = create_engine(url=db_url,echo=True) # echo shows the sql quried running in order

def create_db_and_table():
    SQLModel.metadata.create_all(engine)

create_db_and_table() # initialize the db and create the table if not already exists

def create_payment_record(payment_link_id:str,
                          amount:int):
    
    entry = buyer(payment_link_id=payment_link_id,
                  amount=amount)
    
    print("---intital payment record---")
    print(entry.model_dump_json(exclude_none=True))
    
    with Session(engine) as session:
        session.add(entry)
        session.commit()

def update_payment_status(payment_link_id:str,
                          payment_id:str,
                          status:str):
    
    with Session(engine) as session:
        statement = select(buyer).where(buyer.payment_link_id == payment_link_id)
        update = session.exec(statement).first()
        
        if update:
            
            update.payment_id = payment_id
            update.status = status
            
            print("---updated payment record with status---")
            print(update.model_dump_json(exclude_none=True))
            
            session.add(update)
            session.commit()
            
            print('Updates the Payent status ✅')
        else:
            print("Payment link id not found ❌")
        

def fetch_oneColumnFirstRow(column:str) -> List[str]:
    
    selected_column = getattr(buyer,column) # buyer.<column>
    
    with Session(engine) as session:
        
        statement = (select(selected_column))
        output = session.exec(statement).first()
        
        return output   

def fetch_paymentStatusByLinkID(payment_link_id:str) -> List[str]:
    
    with Session(engine) as session:
        
        statement = (select(buyer).where(buyer.payment_link_id== payment_link_id))
        output = session.exec(statement).first()
        if output:
            return output.status   