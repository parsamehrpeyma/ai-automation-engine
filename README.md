A Modern FastAPI Backend for Web Scraping, AI-Powered Text Processing, Job Analysis, and Automation Pipelines
⭐ Overview

AI Automation Engine is a powerful backend system built with Python, FastAPI, Playwright, and modern AI/NLP tools.
It provides automated solutions for:

Web scraping

Data extraction

Text cleaning

AI summarization

Keyword extraction

Sentiment analysis

Job posting analysis

CSV/JSON report generation

This project is designed for business automation, data analysis, AI workflows, and job-market intelligence — making it ideal for startups, researchers, and professionals needing clean data fast.

🚀 Features
✅ 1. Web Scraping Engine

Built on Playwright for high-accuracy scraping

Extracts readable text from any public URL

Exports to CSV with line indexing + full URL tracking

✅ 2. AI Text Processing Suite

Summarization

Translation

Keyword extraction

Text cleaning

Language detection

✅ 3. Job Analyzer (AI-Powered)

Extracts insights from job postings:

Required skills

Tech stack

Languages

Summary

“Job fit score” (custom algorithm)

Perfect for building an automated job-hunting system for Europe.

✅ 4. Data Reporting Tools

Generates:

TXT reports

JSON reports

CSV files
with metadata + joke-of-the-day API fun integration 😄

✅ 5. REST API with Swagger UI

Automatic documentation at:

http://127.0.0.1:8000/docs

📁 Project Structure
ai-automation-engine/
│
├── api.py                → FastAPI backend (main application)
├── tools/                → All utilities
│   ├── scraper.py        → Basic scraper
│   ├── scraper_playwright.py → Playwright scraper
│   ├── cleaner.py        → Text cleaner
│   ├── ai_tools.py       → Summary, translation, NLP
│   ├── text_stats.py     → Word/character count
│   ├── job_analyzer.py   → Job analysis pipeline
│   ├── sentiment.py      → Sentiment analysis engine
│   ├── report_generator.py → TXT/JSON/CSV report creators
│   ├── logger.py         → Request logger
│   └── json_logger.py    → JSON-based logger
│
├── data/                 → Auto-generated reports + CSV files
│
├── README.md             → (This File)
└── requirements.txt      → Dependencies

🔧 Installation

Clone the project:

git clone https://github.com/parsamehrpeyma/ai-automation-engine.git
cd ai-automation-engine


Create a virtual environment:

python -m venv venv


Activate it:

Windows:

venv\Scripts\activate


Install dependencies:

pip install -r requirements.txt


Install Playwright:

playwright install


Run the API:

uvicorn api:app --reload


Open your browser:

http://127.0.0.1:8000/docs

🧠 Endpoints Overview
🔹 1. Web Scraping

POST /scrape_url
Scrapes readable text using Playwright.

POST /scrape_to_csv
Exports full text into a structured CSV file.

🔹 2. AI Text Tools

POST /summarize
POST /translate
POST /ai_report

🔹 3. URL Intelligence

POST /analyze_url_ai
Summaries, keywords, translations, stats.

🔹 4. Job Market Tools

POST /analyze_job
Extracts skills, languages, and job-fit score.

🔹 5. Sentiment Analysis

POST /sentiment_ai
Language-aware sentiment detection.

📊 Example: CSV Output (scrape_to_csv)
index	url	line
1	https://www.python.org
	Welcome to Python.org
2	https://www.python.org
	Get started with Python
...	...	...

CSV is generated in:

/data/scrape_<uuid>.csv

🤖 Use Cases
🔥 For Businesses

Competitor analysis

SEO content extraction

Automated reporting

Blog/article scraping

🔥 For Researchers

Dataset collection

NLP preprocessing

Text analysis

🔥 For Job Seekers

Auto-analyze job postings

Extract required skills

Compare opportunities

🔥 For Developers

Backend automation

AI-powered workflows

Custom FastAPI services

🧩 Skills Demonstrated (Great for Resume/Migration)

This project shows hands-on experience with:

Python

FastAPI

Playwright

Web Scraping

NLP

AI summarization

API design

Automation engineering

Data processing

Backend architecture

Text analytics

CSV/JSON pipelines

Perfect for applications to:

🇨🇭 Switzerland
🇳🇴 Norway
🇸🇪 Sweden
🇩🇰 Denmark
🇩🇪 Germany
🇳🇱 Netherlands
🇬🇧 UK

📈 Future Enhancements

Add caching system

Add frontend dashboard

Add OAuth login

Add scheduled job radar automation

Deploy to cloud (Render / Railway / AWS)

📜 License

MIT License
