from datetime import datetime

def log_request(raw_text, cleaned_text):
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"[{time}] RAW: {raw_text} | CLEANED: {cleaned_text}\n"

    with open("logs/requests.log", "a", encoding="utf-8") as f:
        f.write(line)
