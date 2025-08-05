from kafka import KafkaProducer
import json
import os

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

def log_event(event_type: str, data: dict):
    if not KAFKA_ENABLED:
        return
    try:
        log_entry = {"type": event_type, **data}
        producer.send(KAFKA_TOPIC, log_entry)
    except Exception as e:
        print(f"[KAFKA] Failed to log event: {e}")
