import json
import csv
from datetime import datetime

def save_txt(cleaned, chars, words, setup, punchline):
    filename = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Cleaned: {cleaned}\n")
        f.write(f"Characters: {chars}\n")
        f.write(f"Words: {words}\n")
        f.write(f"Joke: {setup} - {punchline}\n")
    return filename


def save_json(cleaned, chars, words, setup, punchline):
    filename = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    data = {
        "cleaned": cleaned,
        "characters": chars,
        "words": words,
        "joke_setup": setup,
        "joke_punchline": punchline
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return filename


def save_csv(cleaned, chars, words, setup, punchline):
    filename = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["cleaned", "characters", "words", "joke_setup", "joke_punchline"])
        writer.writerow([cleaned, chars, words, setup, punchline])
    return filename
