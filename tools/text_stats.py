def get_text_stats(text):
    text = text.strip()
    if not text:
        return 0, 0

    words = text.split()
    num_chars = len(text)
    num_words = len(words)

    return num_chars, num_words
