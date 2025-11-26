def clean_text(text):
    text = text.strip().lower()
    parts = text.split()
    return " ".join(parts)

