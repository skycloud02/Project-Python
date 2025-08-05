from pydantic import BaseModel, ConfigDict
from datetime import datetime

class OperationRequest(BaseModel):
    operation: str
    operand: int

class OperationResponse(OperationRequest):
    result: float
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)