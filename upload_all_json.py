import os
import time
import requests
import json
from datetime import datetime

LOKI_URL = "http://localhost:3100/loki/api/v1/push"
MAX_BATCH_SIZE = 4 * 1024 * 1024  # 4MB

def parse_timestamp(log_line):
    try:
        obj = json.loads(log_line)
        if "ts" in obj:
            if isinstance(obj["ts"], (float, int)):
                return str(int(float(obj["ts"]) * 1e9))
            elif isinstance(obj["ts"], str):
                dt = datetime.fromisoformat(obj["ts"].replace("Z", "+00:00"))
                return str(int(dt.timestamp() * 1e9))
    except:
        pass
    return str(int(time.time() * 1e9))

def send_batch_to_loki(batch):
    payload = {"streams": batch}
    resp = requests.post(LOKI_URL, json=payload)
    if resp.status_code == 204:
        print("✅ Batch uploaded.")
        return True
    else:
        print(f"❌ Error: {resp.status_code} - {resp.text}")
        if resp.status_code == 429:
            time.sleep(1)  # 백오프
        return False

def send_file_to_loki(file_path, label_key, label_val):
    batch = []
    batch_size = 0
    stream = {"stream": {label_key: label_val}, "values": []}

    with open(file_path, 'r') as f:
        for line in f:
            ts = parse_timestamp(line)
            entry = [ts, line.strip()]
            estimated_size = len(ts) + len(line) + 50

            if batch_size + estimated_size > MAX_BATCH_SIZE:
                batch.append(stream)
                if not send_batch_to_loki(batch):
                    return
                batch = []
                stream = {"stream": {label_key: label_val}, "values": []}
                batch_size = 0

            stream["values"].append(entry)
            batch_size += estimated_size

    if stream["values"]:
        batch.append(stream)
        send_batch_to_loki(batch)

def main(directory):
    label_key = "source"
    for filename in os.listdir(directory):
        if filename.endswith(".jsonl"):
            full_path = os.path.join(directory, filename)
            label_val = filename.replace(".jsonl", "")
            print(f"Uploading {filename} as {label_key}='{label_val}'...")
            send_file_to_loki(full_path, label_key, label_val)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python upload_all_jsonl.py /path/to/jsonl_directory")
        sys.exit(1)
    main(sys.argv[1])
