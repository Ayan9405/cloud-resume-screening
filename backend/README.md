# /backend - Serverless AI Resume & Document Screening Pipeline

> **Team Member:** Baibhab Sarkar (GitHub: @Baibhabsarkar41)  
> **Role:** Cloud Backend & Machine Learning Engineer  
> **Stack:** Python 3.11+, AWS Lambda, Amazon S3, Amazon Textract, Amazon Comprehend, Amazon DynamoDB, FastAPI, Scikit-Learn

---

## 🎯 Architecture & Responsibilities

The backend service is an event-driven serverless pipeline designed to automatically parse, extract, evaluate, and rank uploaded resumes against target job postings.

```
       [S3 Upload Event]               [HTTP REST API via API Gateway]
              │                                      │
              ▼                                      ▼
    s3_trigger_handler.py                  presigned_url_handler.py
              │                            candidates_handler.py
              │                            jobs_handler.py
              ▼                                      │
┌──────────────────────────────┐                     │
│       DocumentParser         │                     │
│  (AWS Textract / Local OCR)  │                     │
└─────────────┬────────────────┘                     │
              ▼                                      ▼
┌──────────────────────────────┐            ┌─────────────────┐
│         NLPExtractor         │            │ DynamoDBService │
│ (Comprehend / Regex / NER)   │            │   (NoSQL CRUD)  │
└─────────────┬────────────────┘            └────────┬────────┘
              ▼                                      │
┌──────────────────────────────┐                     │
│        MatchingEngine        │                     │
│ (TF-IDF Cosine + Skills Sim) ├─────────────────────┘
└──────────────────────────────┘
```

---

## 📁 Directory Structure

```
backend/
├── handlers/
│   ├── __init__.py
│   ├── s3_trigger_handler.py    # S3 ObjectCreated event Lambda handler
│   ├── presigned_url_handler.py # API Gateway POST /upload-url handler
│   ├── candidates_handler.py    # Candidates & Leaderboard API router
│   └── jobs_handler.py          # Job descriptions management API router
├── services/
│   ├── __init__.py
│   ├── document_parser.py       # Textract & local fallback parser (PDF/DOCX)
│   ├── nlp_extractor.py         # Entity & skill extractor (contact, tech taxonomy)
│   ├── matching_engine.py       # TF-IDF cosine similarity & composite scoring
│   └── dynamodb_service.py      # DynamoDB CRUD with local mock fallback
├── sample_data/
│   ├── sample_jobs.json         # Seed job definitions
│   └── sample_resumes.json      # Sample resume texts for tests
├── tests/
│   ├── __init__.py
│   ├── run_tests.py             # Self-contained test suite runner
│   ├── test_document_parser.py
│   ├── test_nlp_extractor.py
│   ├── test_matching_engine.py
│   └── test_api.py
├── local_server.py              # FastAPI server simulating AWS API & S3 locally
├── requirements.txt             # Production runtime dependencies
├── requirements-dev.txt         # Dev and test tooling
└── README.md
```

---

## 🚀 Local Development & Testing

### 1. Run the Local Backend Server
Baibhab, Biswajit, and Ayan can run the entire backend locally with zero AWS spend:

```powershell
# From project root
python backend/local_server.py
```
- API starts at: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`

### 2. Run the Unit Test Suite
```powershell
python backend/tests/run_tests.py
```

---

## 🧠 Scoring Formula

Candidate scores are calculated using a weighted composite formula:

$$\text{Final Score} = (\text{Skill Match} \times 0.45) + (\text{Semantic Match} \times 0.40) + (\text{Experience Match} \times 0.15)$$

- **Skill Match (45%)**: Coverage of mandatory required skills (75%) and preferred skills (25%).
- **Semantic Match (40%)**: Cosine similarity between candidate TF-IDF n-gram vector and job description.
- **Experience Match (15%)**: Ratio of candidate's verified tenure vs minimum required years.
