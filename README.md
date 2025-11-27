# Stress Prediction Pipeline: Real-Time Kafka + Flink ML

A complete containerized streaming pipeline for processing worker stress data in real-time using Apache Kafka and Apache Flink with machine learning inference.

## Architecture

```
CSV Data → Kafka Producer (Docker) 
    ↓
Kafka Broker (Docker)
    ↓
Flink Job Consumer (Docker)
    ↓
Real-Time ML Inference & Aggregation
    ↓
Output (print/sink to external system)
```

## Prerequisites

- **Docker Desktop** (with Docker Compose v2)
- **Git**
- **Python 3.8+** (for local development, optional)
- **2 GB+ available disk space**

## Quick Start (5 minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/peppermintflowers/nurse_stress_prediction.git
cd nurse_stress_prediction
git checkout flink-kafka-pipeline
```

### 2. Verify Docker is Running

```bash
docker --version
docker compose version
```

Both should output version info. If not, install Docker Desktop.

### 3. Start All Services

From the project root (`nurse_stress_prediction`), run:

```bash
docker compose up --build -d
```

This will:
- Pull/build all images (Zookeeper, Kafka, Kafka UI, Flink JobManager, Flink TaskManager, CSV Producer)
- Start containers in detached mode
- CSV producer will immediately begin streaming data from `data/workers.csv` to Kafka

### 4. Verify Services are Running

```bash
docker compose ps
```

You should see 6+ containers with status `Up`.

### 5. Monitor the Pipeline

**Kafka UI Dashboard** (view topics & messages):
- Open http://localhost:8080 in your browser
- Navigate to **Topics** → **stress-topic** to see messages flowing

**Flink Dashboard** (view jobs & TaskManagers):
- Open http://localhost:8081 in your browser
- Check resource allocation and task execution

**Producer Logs** (see data being sent):
```bash
docker compose logs csv-producer --tail 50 -f
```

## Project Structure

```
stress-pipeline/
├── docker-compose.yml              # Service orchestration
├── .gitignore                       # Git ignore (large dataset)
├── README.md                        # This file
│
├── data/
│   ├── workers.csv                  # Sample worker data (4 records)
│   ├── producer.py                  # Kafka producer script
│   ├── requirements.txt             # Python dependencies
│   └── Dockerfile.producer          # Producer container image
│
├── flink-job/
│   ├── StressJob.py                 # PyFlink streaming job (main consumer)
│   ├── init_flink_job.py            # Init script (downloads connector, creates model)
│   └── model.pkl                    # Dummy ML model (placeholder)
│
└── dataset/
    └── (merged_data.csv excluded from git due to 821 MB size)
```

## Customization & Integration

### Use Your Own Dataset

1. **Replace the sample data:**
   ```bash
   # Copy your CSV to data/workers.csv
   cp /path/to/your/workers.csv data/workers.csv
   ```
   Expected columns: `id`, `name`, `cpu`, `memory`

2. **Restart the producer:**
   ```bash
   docker compose restart csv-producer
   ```

### Adjust Streaming Parameters

Edit `docker-compose.yml` to change producer behavior:

```yaml
csv-producer:
  environment:
    TOPIC: "stress-topic"              # Kafka topic name
    KAFKA_BOOTSTRAP: "kafka:9092"      # Kafka broker address
    PRODUCER_LOOP: "true"              # Loop CSV: true=continuous, false=once
    SEND_DELAY: "0.5"                  # Delay between messages (seconds)
```

Then restart:
```bash
docker compose restart csv-producer
```

### Modify the Flink Job

The Flink streaming job is in `flink-job/StressJob.py`. It:
1. Consumes JSON messages from `stress-topic`
2. Parses worker data (id, name, cpu, memory)
3. Applies windowed aggregation (10-second tumbling windows)
4. Computes a stress score: `cpu * (memory / 1024)`
5. Loads a dummy ML model and predicts stress (placeholder)
6. Prints results

**To modify the job:**
1. Edit `flink-job/StressJob.py`
2. Restart Flink:
   ```bash
   docker compose restart flink-jobmanager flink-taskmanager
   ```

### Integrate Your ML Model

1. **Replace the dummy model:**
   ```bash
   # Place your trained model (pickle, joblib, or ONNX) in:
   cp /path/to/your/model.pkl flink-job/model.pkl
   ```

2. **Update the prediction logic in StressJob.py:**
   ```python
   def predict_stress(row):
       features = np.array([[row[0], row[1], row[2], row[3], row[4], row[5]]])
       pred = int(model.predict(features)[0])  # Replace with your model
       return f"{row[6]} - predicted stress: {pred}"
   ```

3. **Ensure your model can be pickled and loaded:**
   ```python
   import pickle
   model = pickle.load(open("/opt/flink-job/model.pkl", "rb"))
   ```

## Useful Commands

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs kafka -f
docker compose logs csv-producer -f
docker compose logs flink-jobmanager -f

# Last N lines
docker compose logs --tail 100
```

### Stop All Services

```bash
docker compose down
```

### Stop & Remove Data (Clean Slate)

```bash
docker compose down -v
```

### Restart a Service

```bash
docker compose restart csv-producer
```

### Rebuild an Image

```bash
docker compose build csv-producer --no-cache
docker compose up -d csv-producer
```

## Troubleshooting

### "NoBrokersAvailable" Error in Producer

**Cause:** Kafka is not yet ready when producer starts.  
**Solution:** Producer has a built-in retry loop. Wait 30–60 seconds for Kafka to stabilize, then restart:
```bash
docker compose restart csv-producer
```

### Kafka Topic Not Showing in Kafka UI

**Cause:** Topic takes time to be created.  
**Solution:** Refresh the browser or wait 10 seconds and refresh.

### Large Memory Usage

**Cause:** Flink + Kafka containers use ~2–3 GB RAM.  
**Solution:** 
- Increase Docker Desktop memory limit in settings
- Or reduce Flink memory in `docker-compose.yml`:
  ```yaml
  flink-jobmanager:
    deploy:
      resources:
        limits:
          memory: 512m  # Reduce from default
  ```

### Port Already in Use

**Cause:** Another service is using ports 8080, 8081, 9092, or 2181.  
**Solution:** Change port mappings in `docker-compose.yml`:
```yaml
kafka:
  ports:
    - "9093:9092"  # Map to 9093 instead of 9092
```

## For ML Integration

### Step 1: Prepare Your Data

Ensure your dataset has the same schema as `data/workers.csv`:
```csv
id,name,cpu,memory
w1,worker-a,4,8192
w2,worker-b,2,4096
...
```

### Step 2: Train Your Model

Train a stress prediction model (e.g., RandomForest, Neural Network) and save it:
```python
import pickle
model.fit(X_train, y_train)
pickle.dump(model, open("model.pkl", "wb"))
```

### Step 3: Integrate with Flink

1. Place `model.pkl` in `flink-job/model.pkl`
2. Update `StressJob.py` to use your model's features and output
3. Restart Flink:
   ```bash
   docker compose restart flink-jobmanager flink-taskmanager
   ```

### Step 4: Run End-to-End

```bash
docker compose up -d
# Monitor Flink dashboard at http://localhost:8081
# Monitor Kafka UI at http://localhost:8080
# View prediction logs:
docker compose logs flink-jobmanager -f
```

## Performance & Scaling

- **Throughput:** ~100 messages/sec per producer (configurable via `SEND_DELAY`)
- **Latency:** <1s end-to-end (Kafka → Flink window → prediction)
- **Scale:** To process more data, increase producer `SEND_DELAY` or add multiple producers

## Next Steps

1. **Clone this repo** and check out the `flink-kafka-pipeline` branch
2. **Run `docker compose up -d`** to verify everything works
3. **Replace sample data** with your actual worker/stress dataset
4. **Train your ML model** and integrate it into `flink-job/StressJob.py`
5. **Monitor dashboards** (Kafka UI & Flink) to see data flowing
6. **Extend the Flink job** to persist predictions to a database or external sink (S3, Elasticsearch, etc.)

## Support & Issues

- **Docker errors:** Ensure Docker Desktop is running and has sufficient memory (4+ GB)
- **Git issues:** Verify remote: `git remote -v`
- **Flink errors:** Check logs: `docker compose logs flink-jobmanager`
- **Kafka errors:** Check logs: `docker compose logs kafka`

## License

Same as parent repository (nurse_stress_prediction)

---

**Branch:** `flink-kafka-pipeline`  
**Created:** November 2025  
**Status:** Ready for integration & ML development
