📌 Automation API — Text & Document AI Service

A production-grade FastAPI service designed for text processing, document automation, NLP-based operations, and AI-assisted analysis.

This project showcases expertise in modern Python backend development, FastAPI, asynchronous programming, and AI-powered automation workflows — all essential skills for high-level engineering roles in Europe (Norway, Switzerland, Netherlands) and global tech companies.

🚀 Features
✔ Text Processing

Text cleaning & normalization

Character & word statistics

NLP-ready cleaned output

✔ AI-Powered Tools

Text Summarization (HuggingFace Transformers)

Machine Translation (Google Translate API)

Automatic Joke Generator (public API, async safe)

✔ File Handling & Automation

Upload and analyze TXT files

Upload and extract text from PDF documents

Auto-generated structured reports:

TXT

JSON

CSV

✔ Logging & Monitoring

Request logging (requests.log)

Structured JSON logging (requests.jsonl)

Auto-generated timestamped reports

🧠 Tech Stack
Component	Technology
Backend Framework	FastAPI
Language	Python 3.11+
AI / NLP	Transformers, Torch CPU, HuggingFace
Logging	Built-in Python logging + JSONL logging
File Processing	PyPDF2
API Testing	cURL, Swagger UI, ReDoc
Environment	venv / requirements.txt
🗂 Project Structure
automation_project/
│
├── api.py               # Main API (FastAPI app)
├── main.py              # Standalone runner script
├── requirements.txt     # Dependencies
│
├── tools/
│   ├── ai_tools.py      # Summarization & translation AI
│   ├── cleaner.py       # Text cleaning engine
│   ├── text_stats.py    # Word/char statistics
│   ├── joke_api.py      # External joke integration
│   ├── report_generator.py  # TXT/CSV/JSON report builder
│   ├── logger.py            # Request logger
│   ├── json_logger.py       # JSONL logger
│   └── clean_names.py       # Utilities
│
├── data/                # Input samples
├── logs/                # Request logs
├── reports/             # Generated reports
└── README.md

⚙️ Setup & Installation
1️⃣ Clone the repository
git clone https://github.com/parsamehrpeyma/automation_project.git
cd automation_project

2️⃣ Create virtual environment
python -m venv venv

3️⃣ Activate it

Windows:

venv\Scripts\activate

4️⃣ Install dependencies
pip install -r requirements.txt

▶️ Run the API
uvicorn api:app --reload


Server runs on:
👉 http://127.0.0.1:8000

Swagger UI:
👉 http://127.0.0.1:8000/docs

ReDoc:
👉 http://127.0.0.1:8000/redoc

🧪 Example API Calls
✔ Process Text
curl -X GET "http://127.0.0.1:8000/process?text=Hello+World"

✔ Summarize Text
curl -X POST "http://127.0.0.1:8000/summarize" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Artificial intelligence is transforming global industries...\"}"

✔ Translate Text
curl -X POST "http://127.0.0.1:8000/translate" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"سلام دنیا\", \"target_lang\":\"en\"}"

✔ Upload PDF

Use Swagger UI → /upload_pdf

🎯 Why This Project Matters (For Hiring Managers)

This API demonstrates:

🔥 Production-level backend engineering:

Clean code architecture

Modular tools & reusable components

Error handling + logging + reporting

RESTful, well-documented endpoints

🔥 Real AI/NLP integration:

Working with HuggingFace models

Pipeline optimization (CPU-friendly)

Automatic summarization & translation

🔥 Automation mindset:

Converting text → structured data

Turning documents into machine-readable reports

Programmatic workflows

This is a practical, resume-ready project fully aligned with backend engineering and AI-automation roles in Europe and global companies.

🧩 Future Improvements (Planned)

JWT Authentication

Docker deployment

CI/CD pipeline (GitHub Actions)

Redis caching for AI models

Frontend dashboard (React/Vue)

👤 Author

Parsa Mehrpeyma
Python Developer • AI Automation Engineer
GitHub: https://github.com/parsamehrpeyma