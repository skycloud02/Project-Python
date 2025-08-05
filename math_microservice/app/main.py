from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.crud.crud import save_operation, get_all_operations
from app.database.database import get_db, engine, Base
from app.schemas.schemas import OperationRequest, OperationResponse
from app.utils.utils import compute_operation
from app.utils.cache import get_cached_result, set_cached_result
from fastapi.security import APIKeyHeader
from fastapi import Security
from datetime import datetime
from kafka import KafkaProducer
import json
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Math Operations Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


KAFKA_ENABLED = True
KAFKA_TOPIC = "math_logs"
KAFKA_SERVER = os.getenv("KAFKA_BROKER", "localhost:9092")

try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
except Exception as e:
    print(f"[KAFKA] Connection failed: {e}")
    KAFKA_ENABLED = False

LOG_FILE_PATH = "app/logs/logs.json"
def log_event(event_type: str, data: dict):
    if not KAFKA_ENABLED:
        return
    try:
        log_entry = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **data
        }
        producer.send(KAFKA_TOPIC, log_entry)
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        with open(LOG_FILE_PATH, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"[KAFKA] Failed to log event: {e}")
Base.metadata.create_all(bind=engine)

API_KEY = "super-secret-key"
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

@app.get("/")
def root():
    return {"message": "Welcome to the Math Microservice. Use /docs to explore the API."}

@app.post("/compute", response_model=OperationResponse)
def compute(req: OperationRequest, db: Session = Depends(get_db), _: str = Depends(verify_api_key)):
    try:
        log_event("compute_request", {
            "operation": req.operation,
            "operand": req.operand
        })

        cached = get_cached_result(req.operation, req.operand)
        if cached is not None:
            log_event("cache_hit", {"key": f"{req.operation}:{req.operand}"})
            return OperationResponse(
                operation=req.operation,
                operand=req.operand,
                result=cached,
                timestamp=datetime.utcnow()
            )

        log_event("cache_miss", {"key": f"{req.operation}:{req.operand}"})
        result = compute_operation(req.operation, req.operand)
        set_cached_result(req.operation, req.operand, result)
        db_op = save_operation(db, req.operation, req.operand, result)

        log_event("compute_success", {
            "operation": req.operation,
            "operand": req.operand,
            "result": result,
            "db_id": db_op.id
        })

        return OperationResponse.from_orm(db_op)
    except ValueError as e:
        log_event("compute_validation_error", {"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log_event("compute_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/history", response_model=list[OperationResponse])
def get_history(db: Session = Depends(get_db), _: str = Depends(verify_api_key)):
    log_event("history_request", {})
    return get_all_operations(db)


@app.get("/logs")
def get_logs(_: str = Depends(verify_api_key)):
    log_path = "app/logs/logs.json"
    if not os.path.exists(log_path):
        return []
    try:
        with open(log_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            logs = []
            for line in lines[-50:]:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"[LOG ERROR] Skipping bad log line: {line}")
            return logs
    except Exception as e:
        print("[LOG FILE ERROR]", e)
        return JSONResponse(status_code=500, content={"error": str(e)})

