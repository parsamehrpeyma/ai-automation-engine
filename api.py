from tools.ai_tools import summarize_text, translate_text

import io
from PyPDF2 import PdfReader

from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel

from tools.cleaner import clean_text
from tools.text_stats import get_text_stats
from tools.joke_api import get_joke
from tools.report_generator import save_txt, save_json, save_csv
from tools.json_logger import log_json
from tools.logger import log_request
from tools.ai_tools import summarize_text, translate_text, analyze_sentiment


# -------------------------
# Pydantic Models
# -------------------------
class AIReportRequest(BaseModel):
    text: str
    translate_to: str | None = None  # مثلا "en" یا "fa"؛ اگر None باشه ترجمه انجام نمیشه


class AIReportResponse(BaseModel):
    cleaned: str
    characters: int
    words: int
    summary: str
    joke_setup: str
    joke_punchline: str
    translated: str | None
    reports: dict


class TextRequest(BaseModel):
    text: str


class ProcessResponse(BaseModel):
    cleaned: str
    characters: int
    words: int
    joke_setup: str
    joke_punchline: str
    report_txt: str
    report_json: str
    report_csv: str


class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "en"  # پیش‌فرض: ترجمه به انگلیسی

class SentimentRequest(BaseModel):
    text: str


class SentimentResponse(BaseModel):
    label: str
    score: float
    note: str

# -------------------------
# FastAPI App
# -------------------------

app = FastAPI()


# -------------------------
# Basic health check
# -------------------------

@app.get("/")
def home():
    return {"message": "Automation API is running!"}


# -------------------------
# Simple GET processing
# -------------------------

@app.get("/process")
def process(text: str):
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
# Simple analyze only
# -------------------------

@app.post("/analyze_only")
def analyze_only(payload: TextRequest):
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
    text = payload.text

    if len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text too short.")

    summary = summarize_text(text)

    return {
        "original": text,
        "summary": summary,
    }


# -------------------------
# Translation endpoint
# -------------------------

@app.post("/translate")
def translate(payload: TranslateRequest):
    """
    ترجمه‌ی متن به زبان هدف.
    مثال target_lang:
    - "en" برای انگلیسی
    - "fa" برای فارسی
    - "de" برای آلمانی
    - "fr" برای فرانسوی
    """
    data = translate_text(payload.text, payload.target_lang)

    return {
        "source_lang": data["source_lang"],
        "target_lang": data["target_lang"],
        "original": data["original"],
        "translated": data["translated"],
    }
@app.post("/ai_report", response_model=AIReportResponse)
def ai_report(payload: AIReportRequest):
    raw_text = payload.text

    if len(raw_text.strip()) < 3:
        raise HTTPException(status_code=400, detail="Text is too short.")

    # 1) تمیز کردن متن
    cleaned = clean_text(raw_text)

    # 2) آمار متن
    num_chars, num_words = get_text_stats(cleaned)

    # 3) خلاصه متن
    summary = summarize_text(cleaned)

    # 4) گرفتن جوک
    try:
        setup, punchline = get_joke()
    except Exception:
        setup, punchline = "", ""

    # 5) ترجمه (اگر کاربر خواسته باشد)
    translated_text = None
    if payload.translate_to:
        t = translate_text(cleaned, payload.translate_to)
        translated_text = t["translated"]

    # 6) ساخت گزارش‌ها
    txt_path = save_txt(cleaned, num_chars, num_words, setup, punchline)
    json_path = save_json(cleaned, num_chars, num_words, setup, punchline)
    csv_path = save_csv(cleaned, num_chars, num_words, setup, punchline)

    reports = {
        "txt": txt_path,
        "json": json_path,
        "csv": csv_path,
    }

    # 7) خروجی نهایی
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
@app.post("/sentiment", response_model=SentimentResponse)
def sentiment(payload: SentimentRequest):
    """
    تحلیل احساس متن (فعلاً برای انگلیسی دقیق است).
    """
    data = analyze_sentiment(payload.text)

    return SentimentResponse(
        label=data["label"],
        score=data["score"],
        note=data["note"],
    )
