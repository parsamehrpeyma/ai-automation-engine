from tools.cleaner import clean_text
from tools.text_stats import get_text_stats
from tools.joke_api import get_joke

# 1) خواندن فایل ورودی
with open("data/input.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# 2) تمیز کردن متن
cleaned = clean_text(raw_text)

# 3) تحلیل متن
num_chars, num_words = get_text_stats(cleaned)

# 4) گرفتن جوک از اینترنت
setup, punchline = get_joke()

# 5) ساخت گزارش
report = f"""
=== AUTOMATION REPORT ===

Raw Text:
{raw_text}

Cleaned Text:
{cleaned}

Characters: {num_chars}
Words: {num_words}

=== RANDOM JOKE FROM API ===
{setup}
{punchline}

"""

# 6) ذخیره گزارش
with open("data/report.txt", "w", encoding="utf-8") as f:
    f.write(report)

print("Automation completed. Report saved in data/report.txt")
