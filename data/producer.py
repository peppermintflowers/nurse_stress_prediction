import os
import csv
import time
import json
import avro.schema
import avro.io
from kafka import KafkaProducer
from io import BytesIO
from kafka.admin import KafkaAdminClient

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.getenv("TOPIC", "stress-topic")
DELAY = float(os.getenv("SEND_DELAY", "0.5"))
CSV_PATH = os.getenv("CSV_PATH", "/data/workers.csv")
LOOP = os.getenv("PRODUCER_LOOP", "false").lower() in ("1", "true", "yes")
SCHEMA_PATH = "/data/nurse_sensor_event.avsc"

def wait_for_bootstrap(bootstrap, timeout=3, retries=60):
    import socket
    host, port = bootstrap.split(",")[0].split(":")
    port = int(port)

    for attempt in range(retries):
        try:
            with socket.create_connection((host, port), timeout=timeout):
                print(f"Connected to Kafka at {host}:{port}")
                return
        except Exception:
            print(f"Waiting for Kafka at {host}:{port} (attempt {attempt+1})")
            time.sleep(1.0)

    raise RuntimeError(f"Could not connect to Kafka at {host}:{port}")

def ensure_topic_exists(topic_name):
    admin_client = KafkaAdminClient(bootstrap_servers=BOOTSTRAP)
    existing_topics = admin_client.list_topics()
    if topic_name not in existing_topics:
        raise RuntimeError(f"Topic '{topic_name}' does not exist! Exiting.")
    print(f"Topic '{topic_name}' exists. Proceeding...")

wait_for_bootstrap(BOOTSTRAP)
ensure_topic_exists(TOPIC)


schema = avro.schema.parse(open(SCHEMA_PATH, "r").read())

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP,
    value_serializer=lambda v: v
)

def encode_avro(record, schema):
    bytes_writer = BytesIO()
    encoder = avro.io.BinaryEncoder(bytes_writer)
    writer = avro.io.DatumWriter(schema)
    writer.write(record, encoder)
    return bytes_writer.getvalue()



def send_once():
    print("Starting CSV streaming...")

    with open(CSV_PATH, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            avro_record = {
                "X": float(row["X"]) if row["X"] else None,
                "Y": float(row["Y"]) if row["Y"] else None,
                "Z": float(row["Z"]) if row["Z"] else None,
                "EDA": float(row["EDA"]) if row["EDA"] else None,
                "HR": float(row["HR"]) if row["HR"] else None,
                "TEMP": float(row["TEMP"]) if row["TEMP"] else None,
                "id": int(row["id"]) if row["id"] else None,
                "datetime": row["datetime"] if row["datetime"] else None
            }

            payload = encode_avro(avro_record, schema)

            producer.send(
                TOPIC,
                key=str(avro_record["id"]).encode("utf-8"),
                value=payload
            )

            print("sent:", avro_record)

            time.sleep(DELAY)

    producer.flush()


if LOOP:
    while True:
        send_once()
        time.sleep(1.0)
else:
    send_once()
