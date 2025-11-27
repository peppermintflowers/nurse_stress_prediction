import os
import csv
import time
import json
from kafka import KafkaProducer

# Configuration via environment variables (works inside Docker Compose)
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.getenv("TOPIC", "stress-topic")
DELAY = float(os.getenv("SEND_DELAY", "0.5"))

# Wait until Kafka bootstrap server is reachable (avoid race at container start)
def wait_for_bootstrap(bootstrap, timeout=3, retries=60):
    import socket
    parts = bootstrap.split(',')[0].split(':')
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 9092
    attempt = 0
    while attempt < retries:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                print(f"Connected to Kafka at {host}:{port}")
                return True
        except Exception:
            attempt += 1
            print(f"Waiting for Kafka at {host}:{port} (attempt {attempt})")
            time.sleep(1.0)
    raise RuntimeError(f"Could not connect to Kafka at {host}:{port} after {retries} attempts")

wait_for_bootstrap(BOOTSTRAP)

# now that Kafka is reachable, create the producer
producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

csv_path = os.getenv("CSV_PATH", "/data/workers.csv")
LOOP = os.getenv("PRODUCER_LOOP", "false").lower() in ("1", "true", "yes")

def send_once():
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            producer.send(TOPIC, value=row)
            print("sent:", row)
            time.sleep(DELAY)
    producer.flush()

if LOOP:
    while True:
        send_once()
        # small pause between full passes
        time.sleep(1.0)
else:
    send_once()
