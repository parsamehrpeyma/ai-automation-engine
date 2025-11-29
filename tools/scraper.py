import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def fetch_html(url: str, timeout: int = 10) -> str:
    """
    گرفتن HTML خام از یک URL.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def extract_main_text(html: str) -> str:
    """
    استخراج متن اصلی از یک صفحه HTML:
    - حذف <script>, <style>, <nav>, <footer>, ...
    - جمع‌کردن متن تگ‌های مهم مثل <p>, <h1-3>, <li>
    """
    soup = BeautifulSoup(html, "lxml")

    # حذف اسکریپت‌ها و استایل‌ها و چیزهای اضافی
    for tag in soup(["script", "style", "noscript", "footer", "nav", "header"]):
        tag.decompose()

    # تیترهای اصلی
    parts = []

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    if title:
        parts.append(title)

    # متن پاراگراف‌ها و تیترها
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
        text = tag.get_text(separator=" ", strip=True)
        if text and len(text) > 30:  # چیزهای خیلی کوتاه رو رد می‌کنیم
            parts.append(text)

    main_text = "\n".join(parts)
    return main_text


def get_domain(url: str) -> str:
    """
    گرفتن دامنه اصلی از URL (مثلاً https://example.com/... -> example.com)
    """
    parsed = urlparse(url)
    return parsed.netloc


def scrape_url(url: str) -> dict:
    """
    اسکریپت کامل: HTML + متن استخراج شده + دامنه.
    """
    html = fetch_html(url)
    text = extract_main_text(html)
    domain = get_domain(url)

    return {
        "url": url,
        "domain": domain,
        "html_length": len(html),
        "raw_html": html,
        "extracted_text": text,
    }
