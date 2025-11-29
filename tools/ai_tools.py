import re
import string
from transformers import pipeline
from deep_translator import GoogleTranslator

# ---------------------------
# 1) Summarizer English model
# ---------------------------
try:
    summarizer_en = pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        device=-1  # CPU
    )
    print("Device set to use cpu")
except Exception:
    summarizer_en = None
    print("English AI summarizer failed to load. Using fallback for all languages.")

# ---------------------------
# Sentiment Analysis model (English)
# ---------------------------
try:
    sentiment_en = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=-1  # CPU
    )
    print("English sentiment model loaded.")
except Exception:
    sentiment_en = None
    print("Sentiment model failed to load. Using fallback.")

# ---------------------------
# 2) Check if text mostly English
# ---------------------------
def is_mostly_english(text: str, threshold: float = 0.6) -> bool:
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return False

    english_letters = [ch for ch in letters if ch in string.ascii_letters]
    ratio = len(english_letters) / len(letters)
    return ratio >= threshold


# ---------------------------
# 3) Simple fallback summarizer (for Persian)
# ---------------------------
def simple_summary(text: str, max_sentences: int = 3, max_chars: int = 400) -> str:
    text = text.strip()

    if not text:
        return ""

    if len(text) <= max_chars:
        return text

    sentences = re.split(r'(?<=[\.!\?؟])\s+', text)
    summary_sentences = sentences[:max_sentences]
    summary = " ".join(summary_sentences).strip()

    if len(summary) > max_chars:
        summary = summary[:max_chars]
        last_space = summary.rfind(" ")
        if last_space != -1:
            summary = summary[:last_space]
        summary += "..."

    return summary


# ---------------------------
# 4) Summarize function
# ---------------------------
def summarize_text(text: str) -> str:
    text = text.strip()
    if len(text) < 20:
        return text

    # محدود کردن به مثلا 4000 کاراکتر برای سرعت و پایدار بودن
    MAX_INPUT_CHARS = 4000
    if len(text) > MAX_INPUT_CHARS:
        text = text[:MAX_INPUT_CHARS]

    if summarizer_en is not None and is_mostly_english(text):
        try:
            result = summarizer_en(
                text,
                max_length=150,
                min_length=40,
                do_sample=False
            )
            return result[0]["summary_text"]
        except Exception:
            return simple_summary(text)

    return simple_summary(text)

def analyze_sentiment(text: str) -> dict:
    """
    اگر متن عمدتاً انگلیسی باشد و مدل در دسترس باشد → از مدل استفاده می‌کنیم.
    در غیر این صورت، یه جواب ساده و خنثی می‌دهیم.
    """
    text = text.strip()
    if not text:
        return {
            "label": "NEUTRAL",
            "score": 0.0,
            "note": "Empty text."
        }

    # اگر متن فارسیه یا غیر انگلیسی:
    if sentiment_en is None or not is_mostly_english(text):
        # برای فارسی فعلاً یه حالت ساده برمی‌گردونیم
        return {
            "label": "UNKNOWN",
            "score": 0.0,
            "note": "Sentiment model is English-only. For non-English text, sentiment is not analyzed."
        }

    try:
        result = sentiment_en(text)[0]  # مثل {'label': 'POSITIVE', 'score': 0.99}
        return {
            "label": result["label"],
            "score": float(result["score"]),
            "note": "English sentiment analyzed by AI model."
        }
    except Exception:
        return {
            "label": "ERROR",
            "score": 0.0,
            "note": "Error while running sentiment model."
        }


# ---------------------------
# 5) Translation using deep-translator
# ---------------------------
def translate_text(text: str, target_lang: str = "en") -> dict:
    text = text.strip()

    if not text:
        return {
            "source_lang": None,
            "target_lang": target_lang,
            "original": "",
            "translated": ""
        }

    try:
        # detect language
        source_lang = GoogleTranslator(source='auto', target='en').detect(text)
    except Exception:
        source_lang = "auto"

    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception:
        translated = text

    return {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "original": text,
        "translated": translated
    }
