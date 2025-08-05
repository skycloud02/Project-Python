from sqlalchemy.orm import Session
from app.models.models import Operation

def save_operation(db: Session, operation: str, operand: int, result: float):
    db_op = Operation(operation=operation, operand=operand, result=result)
    db.add(db_op)
    db.commit()
    db.refresh(db_op)
    return db_op

def get_all_operations(db: Session):
    return db.query(Operation).order_by(Operation.timestamp.desc()).all()
