import requests
import csv
import os
from typing import List, Dict, Optional

API_BASE = "http://127.0.0.1:8000"
JOB_URLS_FILE = "job_urls.txt"
OUTPUT_CSV = "job_results.csv"


def load_job_urls(path: str = JOB_URLS_FILE) -> List[str]:
    """
    Load job URLs from a text file.
    Each line in the file should contain a single URL.
    """
    if not os.path.exists(path):
        print(f"[WARN] '{path}' not found. Please create it and add job URLs (one per line).")
        return []

    urls: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if url:
                urls.append(url)

    return urls


def analyze_job_url(job_url: str) -> Optional[Dict]:
    """
    Send a job posting URL to the FastAPI backend (/analyze_job)
    and return the parsed JSON response.
    """
    endpoint = f"{API_BASE}/analyze_job"
    payload = {"url": job_url}

    try:
        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERROR] Failed to analyze job URL '{job_url}': {e}")
        return None


def save_results_to_csv(results: List[Dict], path: str = OUTPUT_CSV) -> None:
    """
    Save a list of job analysis results to a CSV file.
    Each dict in 'results' should contain keys:
    - url, summary, characters, words, skills, languages, tech_stack, job_fit_score
    """
    if not results:
        print("[INFO] No results to save.")
        return

    # Define CSV columns
    fieldnames = [
        "url",
        "characters",
        "words",
        "summary",
        "skills",
        "languages",
        "tech_stack",
        "job_fit_score",
    ]

    # Write CSV
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for item in results:
            writer.writerow({
                "url": item.get("url", ""),
                "characters": item.get("characters", 0),
                "words": item.get("words", 0),
                "summary": item.get("summary", ""),
                "skills": ", ".join(item.get("skills", [])),
                "languages": ", ".join(item.get("languages", [])),
                "tech_stack": ", ".join(item.get("tech_stack", [])),
                "job_fit_score": item.get("job_fit_score", 0),
            })

    print(f"[INFO] Saved {len(results)} job(s) to '{path}'")


def main() -> None:
    print("=== Job Radar v2 ===\n")

    job_urls = load_job_urls()
    if not job_urls:
        print("[INFO] No job URLs loaded. Please add URLs to 'job_urls.txt'.")
        return

    all_results: List[Dict] = []

    for url in job_urls:
        print(f"\nAnalyzing job posting:\n{url}")
        print("-" * 60)

        result = analyze_job_url(url)
        if result is None:
            continue

        # Print a short preview to console
        summary = result.get("summary", "")
        skills = result.get("skills", [])
        languages = result.get("languages", [])
        tech_stack = result.get("tech_stack", [])
        job_fit_score = result.get("job_fit_score", 0)

        print(f"Summary: {summary[:200]}...")
        print(f"Skills: {', '.join(skills) if skills else '-'}")
        print(f"Languages: {', '.join(languages) if languages else '-'}")
        print(f"Tech stack: {', '.join(tech_stack) if tech_stack else '-'}")
        print(f"Job fit score: {job_fit_score}")
        print("-" * 60)

        # Add raw result to list for CSV
        all_results.append(result)

    # Save all results to CSV
    save_results_to_csv(all_results)


if __name__ == "__main__":
    main()
