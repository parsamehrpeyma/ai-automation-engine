import re
import io
import csv
import uuid
import os
from collections import Counter
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from PyPDF2 import PdfReader

from tools.scraper_playwright import scrape_plain_text
from tools.scraper import scrape_url as basic_scrape_url
from tools.cleaner import clean_text
from tools.text_stats import get_text_stats
from tools.joke_api import get_joke
from tools.report_generator import save_txt, save_json, save_csv
from tools.json_logger import log_json
from tools.logger import log_request
from tools.ai_tools import summarize_text, translate_text
from tools.sentiment import analyze_sentiment
from tools.job_analyzer import analyze_job_url


# -------------------------
# Pydantic Models
# -------------------------

class ScrapeRequest(BaseModel):
    """
    Request model for scraping / URL-based endpoints.
    'translate_to' is optional and used by some endpoints.
    """
    url: str
    translate_to: str | None = None  # e.g. "en", "de", "fa"


class TextRequest(BaseModel):
    """
    Generic text-only request body.
    """
    text: str


class URLAIRequest(BaseModel):
    """
    Request model for intelligent URL analysis.
    """
    url: str
    translate_to: str | None = None  # e.g. "en", "de", "fa"


class URLAIResponse(BaseModel):
    """
    Response model for intelligent URL analysis.
    """
    url: str
    domain: str
    characters: int
    words: int
    summary: str
    summary_translated: str | None = None
    keywords: list[str]


class ProcessResponse(BaseModel):
    """
    Response model for basic text processing + generated reports.
    """
    cleaned: str
    characters: int
    words: int
    joke_setup: str
    joke_punchline: str
    report_txt: str
    report_json: str
    report_csv: str


class TranslateRequest(BaseModel):
    """
    Request model for translation.
    """
    text: str
    target_lang: str = "en"


class AIReportRequest(BaseModel):
    """
    Request model for the /ai_report endpoint.
    """
    text: str
    translate_to: str | None = None


class AIReportResponse(BaseModel):
    """
    Response model for /ai_report.
    """
    cleaned: str
    characters: int
    words: int
    summary: str
    joke_setup: str
    joke_punchline: str
    translated: str | None
    reports: dict


class SentimentRequest(BaseModel):
    """
    Request model for sentiment analysis.
    """
    text: str


class SentimentResponse(BaseModel):
    """
    Simple sentiment response model.
    """
    label: str
    score: float
    note: str


class SentimentAPIResponse(BaseModel):
    """
    Response model for /sentiment_ai endpoint.
    """
    language: str
    label: str
    score: float
    translated_text: str | None = None


class JobURLRequest(BaseModel):
    """
    Request model for job analysis.
    The client sends a single job posting URL.
    """
    url: str


class JobAnalysisResponse(BaseModel):
    """
    Response model for /analyze_job endpoint.
    This is a structured view of the job posting.
    """
    url: str
    characters: int
    words: int
    summary: str
    summary_translated: str
    skills: list[str]
    languages: list[str]
    tech_stack: list[str]
    job_fit_score: int


class ScrapeResponse(BaseModel):
    """
    Response model for /scrape_url_ai.
    """
    url: str
    domain: str
    cleaned: str
    characters: int
    words: int
    summary: str
    summary_translated: str | None = None


# -------------------------
# FastAPI App
# -------------------------

app = FastAPI()


# -------------------------
# Health check
# -------------------------

@app.get("/")
def home():
    return {"message": "Automation API is running!"}


# -------------------------
# Simple GET processing
# -------------------------

@app.get("/process")
def process(text: str):
    """
    Simple GET endpoint to process text directly from query param.
    """
    cleaned = clean_text(text)
    num_chars, num_words = get_text_stats(cleaned)
    setup, punchline = get_joke()

    return {
        "cleaned": cleaned,
        "characters": num_chars,
        "words": num_words,
        "joke_setup": setup,
        "joke_punchline": punchline,
    }


# -------------------------
# Main text processing + reports + logging
# -------------------------

@app.post("/process_text", response_model=ProcessResponse)
def process_text(payload: TextRequest):
    """
    Process a text:
    - clean it
    - compute stats
    - generate joke
    - save TXT / JSON / CSV reports
    """
    raw_text = payload.text

    if len(raw_text.strip()) < 3:
        raise HTTPException(status_code=400, detail="Text is too short.")

    cleaned = clean_text(raw_text)

    # logging
    log_request(raw_text, cleaned)
    log_json(raw_text, cleaned)

    num_chars, num_words = get_text_stats(cleaned)

    try:
        setup, punchline = get_joke()
    except Exception:
        setup, punchline = "", ""

    txt_path = save_txt(cleaned, num_chars, num_words, setup, punchline)
    json_path = save_json(cleaned, num_chars, num_words, setup, punchline)
    csv_path = save_csv(cleaned, num_chars, num_words, setup, punchline)

    return ProcessResponse(
        cleaned=cleaned,
        characters=num_chars,
        words=num_words,
        joke_setup=setup,
        joke_punchline=punchline,
        report_txt=txt_path,
        report_json=json_path,
        report_csv=csv_path,
    )


# -------------------------
# Simple analyze-only endpoint
# -------------------------

@app.post("/analyze_only")
def analyze_only(payload: TextRequest):
    """
    Clean text and return only stats (no joke, no reports).
    """
    cleaned = clean_text(payload.text)
    num_chars, num_words = get_text_stats(cleaned)
    return {
        "cleaned": cleaned,
        "characters": num_chars,
        "words": num_words,
    }


# -------------------------
# File upload (plain text)
# -------------------------

@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a plain text file, process its content and generate reports.
    """
    content = (await file.read()).decode("utf-8")

    cleaned = clean_text(content)
    num_chars, num_words = get_text_stats(cleaned)

    try:
        setup, punchline = get_joke()
    except Exception:
        setup, punchline = "", ""

    txt_path = save_txt(cleaned, num_chars, num_words, setup, punchline)
    json_path = save_json(cleaned, num_chars, num_words, setup, punchline)
    csv_path = save_csv(cleaned, num_chars, num_words, setup, punchline)

    return {
        "filename": file.filename,
        "cleaned": cleaned,
        "characters": num_chars,
        "words": num_words,
        "report_txt": txt_path,
        "report_json": json_path,
        "report_csv": csv_path,
    }


# -------------------------
# PDF upload + text extraction
# -------------------------

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF, extract text, process and generate reports.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF.")

    pdf_bytes = await file.read()
    reader = PdfReader(io.BytesIO(pdf_bytes))

    text = ""
    for page in reader.pages:
        extracted = page.extract_text() or ""
        text += extracted + "\n"

    cleaned = clean_text(text)
    num_chars, num_words = get_text_stats(cleaned)

    try:
        setup, punchline = get_joke()
    except Exception:
        setup, punchline = "", ""

    txt_path = save_txt(cleaned, num_chars, num_words, setup, punchline)
    json_path = save_json(cleaned, num_chars, num_words, setup, punchline)
    csv_path = save_csv(cleaned, num_chars, num_words, setup, punchline)

    return {
        "filename": file.filename,
        "cleaned": cleaned,
        "characters": num_chars,
        "words": num_words,
        "report_txt": txt_path,
        "report_json": json_path,
        "report_csv": csv_path,
    }


# -------------------------
# Summarization endpoint
# -------------------------

@app.post("/summarize")
def summarize(payload: TextRequest):
    """
    Summarize a given text.
    """
    text = payload.text

    if len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text too short.")

    summary = summarize_text(text)

    return {
        "original": text,
        "summary": summary,
    }


# -------------------------
# Keyword extractor helper
# -------------------------

def extract_keywords_simple(text: str, top_n: int = 10) -> list[str]:
    """
    Very simple keyword extractor:
    - Lowercase the text
    - Keep only alphabetic tokens with length >= 3
    - Remove common English stopwords
    - Count word frequency
    - Return top N most frequent words
    """

    stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "have", "has",
        "are", "was", "were", "will", "would", "can", "could", "should",
        "about", "into", "onto", "over", "under", "than", "then", "them",
        "they", "you", "your", "yours", "our", "ours", "his", "her", "its",
        "not", "but", "all", "any", "some", "more", "most", "many",
        "such", "very", "also", "just", "like", "one", "two", "three"
    }

    tokens = re.findall(r"[a-zA-Z]{3,}", text.lower())
    filtered = [t for t in tokens if t not in stopwords]
    counts = Counter(filtered)
    return [word for word, _ in counts.most_common(top_n)]


# -------------------------
# Translation endpoint
# -------------------------

@app.post("/translate")
def translate(payload: TranslateRequest):
    """
    Translate a text into a target language.
    Example target_lang:
    - "en" English
    - "fa" Persian
    - "de" German
    - "fr" French
    """
    data = translate_text(payload.text, payload.target_lang)

    return {
        "source_lang": data["source_lang"],
        "target_lang": data["target_lang"],
        "original": data["original"],
        "translated": data["translated"],
    }


# -------------------------
# AI report endpoint
# -------------------------

@app.post("/ai_report", response_model=AIReportResponse)
def ai_report(payload: AIReportRequest):
    """
    Full AI-based report:
    - clean text
    - stats
    - summary
    - joke
    - optional translation
    - TXT/JSON/CSV reports on disk
    """
    raw_text = payload.text

    if len(raw_text.strip()) < 3:
        raise HTTPException(status_code=400, detail="Text is too short.")

    cleaned = clean_text(raw_text)
    num_chars, num_words = get_text_stats(cleaned)
    summary = summarize_text(cleaned)

    try:
        setup, punchline = get_joke()
    except Exception:
        setup, punchline = "", ""

    translated_text = None
    if payload.translate_to:
        t = translate_text(cleaned, payload.translate_to)
        translated_text = t["translated"]

    txt_path = save_txt(cleaned, num_chars, num_words, setup, punchline)
    json_path = save_json(cleaned, num_chars, num_words, setup, punchline)
    csv_path = save_csv(cleaned, num_chars, num_words, setup, punchline)

    reports = {
        "txt": txt_path,
        "json": json_path,
        "csv": csv_path,
    }

    return AIReportResponse(
        cleaned=cleaned,
        characters=num_chars,
        words=num_words,
        summary=summary,
        joke_setup=setup,
        joke_punchline=punchline,
        translated=translated_text,
        reports=reports,
    )


# -------------------------
# Scrape URL + AI (classic version)
# -------------------------

@app.post("/scrape_url_ai", response_model=ScrapeResponse)
def scrape_url_ai(payload: ScrapeRequest):
    """
    Scrape a URL using a basic scraper, clean text,
    summarize and (optionally) translate the summary.
    """
    url = payload.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    try:
        scraped = basic_scrape_url(url)  # aliased scraper from tools.scraper
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping URL: {e}")

    extracted_text = scraped["extracted_text"]
    domain = scraped["domain"]

    if len(extracted_text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Extracted text is too short to analyze.")

    cleaned = clean_text(extracted_text)
    num_chars, num_words = get_text_stats(cleaned)
    summary = summarize_text(cleaned)

    summary_translated = None
    if payload.translate_to is not None and payload.translate_to.strip() != "":
        t = translate_text(summary, payload.translate_to.strip())
        summary_translated = t["translated"]

    return ScrapeResponse(
        url=url,
        domain=domain,
        cleaned=cleaned,
        characters=num_chars,
        words=num_words,
        summary=summary,
        summary_translated=summary_translated,
    )


# -------------------------
# Simple Playwright-based scraper
# -------------------------

@app.post("/scrape_url")
def scrape_url_endpoint(payload: ScrapeRequest):
    """
    Scrape a webpage using Playwright and return readable text.
    """
    url = payload.url.strip()
    text = scrape_plain_text(url)

    return {
        "url": url,
        "text_length": len(text),
        "preview": text[:500],
        "full_text": text
    }


# -------------------------
# Scrape to CSV endpoint (income-oriented)
# -------------------------

@app.post("/scrape_to_csv")
def scrape_to_csv(payload: ScrapeRequest):
    """
    Scrape a webpage using Playwright and save the extracted text into a CSV file.
    Each non-empty line becomes a row in the CSV.
    Returns the relative path to the generated CSV file.
    """
    url = payload.url.strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    # 1) Scrape page using Playwright
    try:
        text = scrape_plain_text(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping URL: {e}")

    if len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Extracted text is too short to save.")

    # 2) Ensure data folder exists
    os.makedirs("data", exist_ok=True)

    # 3) Generate unique filename
    filename = f"scrape_{uuid.uuid4().hex}.csv"
    filepath = os.path.join("data", filename)

        # 4) Save lines into CSV (index, url, line)
    with open(filepath, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["index", "url", "line"])

        index = 1
        for line in text.split("\n"):
            line = line.strip()
            if line:
                writer.writerow([index, url, line])
                index += 1

    # 5) Return path to CSV file
    return {"csv_file": filepath}


# -------------------------
# Intelligent URL analysis
# -------------------------

@app.post("/analyze_url_ai", response_model=URLAIResponse)
def analyze_url_ai(payload: URLAIRequest):
    """
    Full intelligent analysis for a given URL:
    - Scrape readable text using Playwright
    - Clean the text
    - Compute basic stats (characters, words)
    - Summarize the content
    - Optionally translate the summary
    - Extract simple keywords
    """
    url = payload.url.strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    domain = urlparse(url).netloc

    try:
        raw_text = scrape_plain_text(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping URL: {e}")

    if len(raw_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Extracted text is too short to analyze.")

    cleaned = clean_text(raw_text)
    num_chars, num_words = get_text_stats(cleaned)
    summary = summarize_text(cleaned)

    summary_translated: str | None = None
    if payload.translate_to is not None and payload.translate_to.strip() != "":
        try:
            translation_result = translate_text(summary, payload.translate_to.strip())
            summary_translated = translation_result["translated"]
        except Exception:
            summary_translated = None

    keywords = extract_keywords_simple(cleaned, top_n=10)

    return URLAIResponse(
        url=url,
        domain=domain,
        characters=num_chars,
        words=num_words,
        summary=summary,
        summary_translated=summary_translated,
        keywords=keywords,
    )


# -------------------------
# Simple sentiment endpoint
# -------------------------

@app.post("/sentiment", response_model=SentimentResponse)
def sentiment(payload: SentimentRequest):
    """
    Basic sentiment analysis endpoint (simple label/score/note).
    """
    data = analyze_sentiment(payload.text)

    return SentimentResponse(
        label=data["label"],
        score=data["score"],
        note=data["note"],
    )


# -------------------------
# Advanced sentiment endpoint (language-aware)
# -------------------------

@app.post("/sentiment_ai", response_model=SentimentAPIResponse)
def sentiment_ai(payload: SentimentRequest):
    """
    Language-aware sentiment endpoint:
    - Detect language
    - Translate to English if needed
    - Run sentiment model
    - Return language, label, score and translated_text (if used)
    """
    text = payload.text

    if len(text.strip()) < 3:
        raise HTTPException(status_code=400, detail="Text is too short.")

    try:
        result = analyze_sentiment(text)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {e}")

    return SentimentAPIResponse(
        language=result["language"],
        label=result["label"],
        score=result["score"],
        translated_text=result["translated_text"],
    )


# -------------------------
# Job analysis endpoint
# -------------------------

@app.post("/analyze_job", response_model=JobAnalysisResponse)
def analyze_job(payload: JobURLRequest):
    """
    Analyze a job posting from a given URL using the job analyzer tool.
    """
    url = payload.url.strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    result = analyze_job_url(url)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return JobAnalysisResponse(
        url=result["url"],
        characters=result["characters"],
        words=result["words"],
        summary=result["summary"],
        summary_translated=result["summary_translated"],
        skills=result["skills"],
        languages=result["languages"],
        tech_stack=result["tech_stack"],
        job_fit_score=result["job_fit_score"],
    )
