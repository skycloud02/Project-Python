from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database.database import Base  # <-- import Base

class Operation(Base):
    __tablename__ = "operations"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, index=True)
    operand = Column(Integer)
    result = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
