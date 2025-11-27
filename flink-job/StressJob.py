from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.window import TumblingProcessingTimeWindows
from pyflink.common.typeinfo import Types
from pyflink.java_gateway import get_gateway
import json
import pickle
import numpy as np

# load your ML model (trained offline) - ensure model.pkl is mounted at /opt/flink-job/
model = pickle.load(open("/opt/flink-job/model.pkl", "rb"))

env = StreamExecutionEnvironment.get_execution_environment()

# Ensure the Kafka connector JAR is available at /opt/flink-job/flink-connector-kafka.jar
env.add_jars("file:///opt/flink-job/flink-connector-kafka.jar")

# Use the JVM gateway to construct the Java Kafka consumer and properties
gateway = get_gateway()
JProperties = gateway.jvm.java.util.Properties
props = JProperties()
props.setProperty("bootstrap.servers", "kafka:9092")
props.setProperty("group.id", "stress-group")

FlinkKafkaConsumer = gateway.jvm.org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer
SimpleStringSchema = gateway.jvm.org.apache.flink.api.common.serialization.SimpleStringSchema

consumer = FlinkKafkaConsumer("stress-topic", SimpleStringSchema(), props)

# Add the Java consumer as a source and declare returned type
ds = env.add_source(consumer, Types.STRING())

def parse_json(x):
    data = json.loads(x)
    # adapt these fields to match your CSV->Kafka payload
    return (
        float(data.get("X", 0)),
        float(data.get("Y", 0)),
        float(data.get("Z", 0)),
        float(data.get("EDA", 0)),
        float(data.get("HR", 0)),
        float(data.get("TEMP", 0)),
        data.get("id"),
        data.get("datetime"),
        int(data.get("label", 0))
    )

parsed = ds.map(lambda x: parse_json(x), output_type=Types.PICKLED_BYTE_ARRAY())

windowed = (
    parsed
    .key_by(lambda row: row[6])
    .window(TumblingProcessingTimeWindows.of(10000))  # 10s windows
    .reduce(lambda a, b: a)  # placeholder aggregation
)

def predict_stress(row):
    features = np.array([[row[0], row[1], row[2], row[3], row[4], row[5]]])
    pred = int(model.predict(features)[0])
    return f"{row[6]} - predicted stress: {pred}"

# print predicted stress per window
windowed.map(lambda r: predict_stress(r)).print()

env.execute("Stress Prediction Pipeline")
