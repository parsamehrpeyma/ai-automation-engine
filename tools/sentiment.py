import re
from transformers import pipeline
from deep_translator import GoogleTranslator

# Load English sentiment model once
sentiment_en = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# Simple regex to detect Persian characters (Arabic script)
PERSIAN_CHARS = re.compile(r"[\u0600-\u06FF]")


def guess_language(text: str) -> str:
    """
    Very simple language guesser:
    - If it contains Persian/Arabic characters -> "fa"
    - Else if all characters are ASCII -> "en"
    - Else -> "unknown"
    This is not perfect, but it's fast and does not depend on external APIs.
    """
    if PERSIAN_CHARS.search(text):
        return "fa"

    # Check if all characters are basic ASCII
    if all(ord(ch) < 128 for ch in text):
        return "en"

    return "unknown"


def analyze_sentiment(text: str) -> dict:
    """
    Full sentiment analysis pipeline:

    1. Guess language (fa / en / unknown)
    2. If not English -> translate to English (source='auto')
    3. Run English sentiment model on English text
    4. Return:
       - language (our guess)
       - label ("POSITIVE"/"NEGATIVE")
       - score (0.0 - 1.0)
       - translated_text (if non-English input)
    """

    if not text or len(text.strip()) < 3:
        raise ValueError("Text is too short for sentiment analysis.")

    # 1) Guess the language
    lang = guess_language(text)

    # 2) Decide what to send to sentiment model
    english_text = text
    translated_text = None

    if lang != "en":
        # Try to translate from auto-detected source to English
        try:
            english_text = GoogleTranslator(source="auto", target="en").translate(text)
            translated_text = english_text
        except Exception:
            # If translation fails, fall back to original
            english_text = text
            translated_text = None

    # 3) Run sentiment model (truncate long inputs for safety)
    result = sentiment_en(english_text[:512])[0]

    label = result["label"]
    score = float(result["score"])

    # 4) Build result dict
    return {
        "language": lang,
        "label": label,
        "score": score,
        "translated_text": translated_text,
    }
