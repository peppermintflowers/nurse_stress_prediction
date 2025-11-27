# Stress Prediction Pipeline: Real-Time Kafka

A containerized Kafka streaming pipeline for processing worker stress data in real-time. Integrates with Java-based Flink for ML inference.

## Architecture

```
CSV Data → Kafka Producer (Docker) 
    ↓
Kafka Broker (Docker)
    ↓
External Flink Job (Java-based)
    ↓
Real-Time ML Inference & Output
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
- Pull/build all images (Zookeeper, Kafka, Kafka UI, CSV Producer)
- Start containers in detached mode
- CSV producer will immediately begin streaming data from `data/workers.csv` to Kafka

### 4. Verify Services are Running

```bash
docker compose ps
```

You should see 4 containers with status `Up`.

### 5. Monitor the Pipeline

**Kafka UI Dashboard** (view topics & messages):
- Open http://localhost:8080 in your browser
- Navigate to **Topics** → **stress-topic** to see messages flowing

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
│   ├── (Handled by external Java Flink job)
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

### Flink Integration

Your Java Flink job should consume messages from `stress-topic` in Kafka. The messages are in JSON format:

```json
{
  "id": "w1",
  "name": "worker-a",
  "cpu": 4,
  "memory": 8192,
  "datetime": "2025-11-26T10:30:00"
}
```

Kafka is running on `kafka:9092` (internal Docker network) or `localhost:9092` (external).

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

## For ML Integration (Java Flink)

Your Java Flink job receives JSON messages from the `stress-topic` topic. Parse and process them as needed for your stress prediction model.

### Message Format

```json
{
  "id": "w1",
  "name": "worker-a",
  "cpu": 4,
  "memory": 8192,
  "datetime": "2025-11-26T10:30:00"
}
```

### Kafka Connection Details

- **Bootstrap Servers:** `kafka:9092` (Docker network) or `localhost:9092` (local)
- **Topic:** `stress-topic`
- **Consumer Group:** Configure in your Java Flink job
- **Format:** JSON strings

## Performance & Scaling

- **Throughput:** ~100 messages/sec per producer (configurable via `SEND_DELAY`)
- **Latency:** <1s end-to-end (Kafka → Flink window → prediction)
- **Scale:** To process more data, increase producer `SEND_DELAY` or add multiple producers

## Next Steps for Your Team

1. **Clone this repo** and check out the main branch
2. **Run `docker compose up -d`** to start Kafka
3. **Connect your Java Flink job** to `kafka:9092` and consume from `stress-topic`
4. **Process messages** through your ML pipeline
5. **Monitor Kafka UI** at http://localhost:8080 to verify data flow

## Support & Issues

- **Docker errors:** Ensure Docker Desktop is running and has sufficient memory (4+ GB)
- **Git issues:** Verify remote: `git remote -v`
- **Flink errors:** Your Java Flink job handles processing; ensure it can connect to `kafka:9092`
- **Kafka errors:** Check logs: `docker compose logs kafka`

## License

Same as parent repository (nurse_stress_prediction)

---

**Branch:** `main`  
**Created:** November 2025  
**Status:** Kafka streaming ready for external Flink integration
