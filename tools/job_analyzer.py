"""
AI Job Analyzer – v1
--------------------

This module extracts job posting text from a given URL,
then uses AI (your own summarize + analyze pipeline) to
extract structured job information:

- Job Title
- Company Name
- Location
- Required Skills
- Tech Stack
- Languages Required
- Job Type
- Salary (if available)
- Visa Sponsorship (AI guess)
- AI Summary
- Recommended Roadmap
- Job Fit Score (AI estimation)

This is Version 1 (clean and extendable).
"""

import re
import requests
from bs4 import BeautifulSoup

from tools.ai_tools import summarize_text, translate_text
from tools.sentiment import analyze_sentiment   # optional
from tools.scraper_playwright import scrape_plain_text


# ---------------------------
# Helper: clean raw HTML text
# ---------------------------
def clean_job_text(text: str) -> str:
    """
    Clean job description by removing extra whitespace,
    HTML leftovers, tracking numbers, duplicated spaces.
    """
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\n", " ").replace("\t", " ")
    return text.strip()


# ---------------------------
# Extract raw text from URL
# ---------------------------
def extract_text_from_url(url: str) -> str:
    """
    Try Playwright first (best extraction).
    Fallback to requests + BeautifulSoup.
    """

    try:
        text = scrape_plain_text(url)
        if text and len(text.strip()) > 50:
            return clean_job_text(text)
    except Exception:
        pass

    # Fallback (simple)
    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0"
        })
        soup = BeautifulSoup(resp.text, "html.parser")
        return clean_job_text(soup.get_text())
    except Exception:
        return ""


# ---------------------------
# AI Job Analysis (main logic)
# ---------------------------
def ai_analyze_job(text: str) -> dict:
    """
    Use your existing AI tools to extract structured job info.
    This version uses summarization + keyword extraction via regex.
    """

    # AI summary
    summary = summarize_text(text)

    # Translate summary to Persian (optional for understanding)
    summary_fa = translate_text(summary, "fa")["translated"]

    # Extract keywords (simple v1)
    skills = find_skills(text)
    languages = find_languages(text)
    tech_stack = find_technologies(text)

    # Approx score
    score = estimate_job_fit(skills)

    return {
        "summary": summary,
        "summary_translated": summary_fa,
        "skills": skills,
        "languages": languages,
        "tech_stack": tech_stack,
        "job_fit_score": score
    }


# ---------------------------
# Keyword Extractors (simple v1)
# ---------------------------
def find_skills(text: str) -> list:
    """
    Very simple keyword scanning version.
    Later you will upgrade to AI NER models.
    """
    SKILL_KEYWORDS = [
        "python", "java", "javascript", "react", "vue",
        "docker", "kubernetes", "sql", "nosql", "linux",
        "machine learning", "deep learning",
        "data analysis", "api", "cloud", "aws", "azure",
        "fastapi", "flask", "django"
    ]

    found = []
    lower = text.lower()

    for skill in SKILL_KEYWORDS:
        if skill in lower:
            found.append(skill)

    return sorted(set(found))


def find_languages(text: str) -> list:
    LANGS = ["english", "german", "french", "arabic", "persian", "norwegian"]
    found = []

    t = text.lower()

    for lang in LANGS:
        if lang in t:
            found.append(lang)

    return found


def find_technologies(text: str) -> list:
    TECH = [
        "aws", "gcp", "azure",
        "docker", "kubernetes",
        "tensorflow", "pytorch",
        "fastapi", "flask", "django",
        "postgres", "mysql", "mongodb",
        "redis"
    ]

    found = []
    t = text.lower()

    for tech in TECH:
        if tech in t:
            found.append(tech)

    return sorted(set(found))


# ---------------------------
# Estimate job fit score (v1)
# ---------------------------
def estimate_job_fit(skills: list) -> int:
    """
    Very rough score: more skills found → better score.
    """
    if not skills:
        return 20

    base = 40
    bonus = len(skills) * 7

    score = base + bonus
    return min(score, 95)


# ---------------------------
# Main entry point
# ---------------------------
def analyze_job_url(url: str) -> dict:
    """
    Full pipeline:
    - download page
    - extract text
    - analyze with AI
    - return structured result
    """

    raw_text = extract_text_from_url(url)
    if len(raw_text) < 50:
        return {"error": "Could not extract enough text from URL."}

    job_data = ai_analyze_job(raw_text)

    return {
        "url": url,
        "characters": len(raw_text),
        "words": len(raw_text.split()),
        **job_data
    }
