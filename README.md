# Loki JSONL Log Ingestion

This project provides a complete pipeline to ingest `.jsonl`-formatted logs into [Grafana Loki](https://grafana.com/oss/loki/) using [Promtail](https://grafana.com/docs/loki/latest/clients/promtail/), and visualize them in [Grafana](https://grafana.com/oss/grafana/).

## 🛠️ Features

- Ingest `.jsonl` structured logs via custom Python script  
- Pre-configured `docker-compose` setup for Loki, Promtail, and Grafana  
- Real-time log visualization in Grafana Explore  
- Supports ingestion of large datasets with rate limit management  

## 📦 Project Structure

```
.
├── by_source/                  # Sample JSONL log files
├── docker-compose.yml          # Loki, Promtail, Grafana services
├── loki-config.yaml            # Loki configuration
├── promtail-config.yaml        # Promtail configuration
├── upload_all_jsonl.py         # Python uploader for JSONL files
```

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/loki-jsonl-log-ingestion.git
cd loki-jsonl-log-ingestion
```

### 2. Launch the Stack

```bash
sudo docker-compose up -d
```

This will start:
- Loki (default port: `3100`)
- Promtail (default port: `9080`)
- Grafana (default port: `3000`)

### 3. Upload JSONL Logs to Loki

```bash
python3 upload_all_jsonl.py ./by_source/
```

> ⚠️ Note: Some files may exceed the default Loki ingestion limit (e.g., 4MB). You'll need to split or downsample large files or adjust Loki's limits in the configuration.

### 4. Access Grafana

- Visit [http://localhost:3000](http://localhost:3000)
- Default credentials:
  - **Username:** `admin`
  - **Password:** `admin` (you'll be prompted to change it)

### 5. Explore Logs

- Go to **Explore**
- Select **Loki** as the data source
- Use queries like:
  ```logql
  {job="files"}
  ```

## ⚙️ Configuration Notes

- Promtail is configured to tail files in `/var/log/*.log` and ingest sample `.jsonl` logs
- You can customize `promtail-config.yaml` to change file targets or relabel log streams

## 🧩 Troubleshooting

- **500 ResourceExhausted**: File exceeds maximum allowed size (default 4MB). Try chunking the data.
- **429 Rate limit exceeded**: Too many log entries per second. Use `time.sleep()` or chunk uploads.
- Use `curl http://localhost:3100/ready` to verify Loki is ready.
- Use `docker-compose logs` to debug individual service logs.
