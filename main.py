from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, String, Integer, JSON, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Union

# Database setup
DATABASE_URL = "postgresql://transaction_mocks_user:px1uZjvc2MHpNLUOj2tAv7cG3Lt1ntnf@dpg-cm4ra78cmk4c73cls50g-a.oregon-postgres.render.com/transaction_mocks"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, index=True)
    data = Column(JSON)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to fetch stored JSON data
@app.get("/fetch/{id}")
async def fetch_transactions(id: Union[str], db: Session = Depends(get_db)):
    stored_data = db.query(Transaction).filter(Transaction.id == id).first().data
    if not stored_data:
        raise HTTPException(status_code=404, detail="Data not found")
    return stored_data

# Combined create/update endpoint
@app.post("/update/{id}")
async def update_transactions(id: Union[str], data: dict, db: Session = Depends(get_db)):
    existing_transaction = db.query(Transaction).filter(Transaction.id == id).first()

    if existing_transaction:
        # Update existing transaction
        for key, value in data.items():
            setattr(existing_transaction, key, value)
    else:
        # Create new transaction
        new_transaction = Transaction(id=id, **data)
        db.add(new_transaction)

    db.commit()
    return {"message": "Transaction created/updated successfully"}
