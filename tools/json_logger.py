import json
from datetime import datetime

def log_json(raw_text, cleaned_text):
    entry = {
        "time": datetime.now().isoformat(),
        "raw": raw_text,
        "cleaned": cleaned_text
    }

    with open("logs/requests.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
