import os
import time
import requests

LOKI_URL = "http://localhost:3100/loki/api/v1/push"
MAX_BATCH_SIZE = 4 * 1024 * 1024 
SLEEP_BETWEEN_BATCHES = 1 

def send_batch_to_loki(batch, job_label):
    payload = {"streams": batch}
    resp = requests.post(LOKI_URL, json=payload)
    if resp.status_code == 204:
        print(f"Uploaded batch successfully.")
        return True
    else:
        print(f"Failed to upload batch: {resp.status_code}, {resp.text}")
        return False

def send_file_to_loki(file_path, job_label):
    batch = []
    batch_size = 0

    stream = {
        "stream": {"job": job_label},
        "values": []
    }

    with open(file_path, 'r') as f:
        for line in f:
            ts = str(int(time.time() * 1e9))
            entry = [ts, line.strip()]
            estimated_entry_size = len(ts) + len(line) + 50

            if batch_size + estimated_entry_size > MAX_BATCH_SIZE:
                batch.append(stream)
                success = send_batch_to_loki(batch, job_label)
                if not success:
                    print("Stopping upload due to error.")
                    return
                time.sleep(SLEEP_BETWEEN_BATCHES)
                batch = []
                stream = {
                    "stream": {"job": job_label},
                    "values": []
                }
                batch_size = 0

            stream["values"].append(entry)
            batch_size += estimated_entry_size

    if stream["values"]:
        batch.append(stream)
        send_batch_to_loki(batch, job_label)

def main(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".jsonl"):
            full_path = os.path.join(directory, filename)
            job_label = filename.replace(".jsonl", "")
            print(f"Uploading {filename} as job '{job_label}'...")
            send_file_to_loki(full_path, job_label)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python upload_all_jsonl.py /path/to/jsonl_directory")
        sys.exit(1)
    main(sys.argv[1])
