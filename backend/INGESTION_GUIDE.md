# YAMA AI — Legal Knowledge Ingestion System
## Complete Setup & Run Guide

---

## System Overview

```
Internet Sources
      ↓
 Crawler Modules
      ↓
HTML Downloader + Parser
      ↓
Section Detection + Data Cleaner
      ↓
Metadata Tagging + Keywords
      ↓
Structured JSON (laws.json, constitution.json, ...)
      ↓
PostgreSQL / SQLite Database
      ↓
Embedding Generator (sentence-transformers)
      ↓
ChromaDB Vector Database
```

---

## Project Structure

```
backend/
├── data_pipeline/
│   ├── crawler_constitution.py    ← Constitution of India crawler
│   ├── crawler_central_laws.py    ← India Code / Central Acts crawler
│   ├── crawler_state_laws.py      ← State legislation crawler
│   ├── crawler_court_judgments.py ← SC & HC judgment crawler
│   ├── crawler.py                 ← Unified crawler (legacy)
│   ├── parser.py                  ← Legal text parser
│   ├── cleaner.py                 ← Data cleaner
│   ├── scheduler.py               ← Ingestion scheduler (legacy)
│   └── datasets/
│       ├── constitution.json      ← Constitution dataset (30+ articles)
│       ├── laws.json              ← Central Acts dataset (30+ sections)
│       ├── state_laws.json        ← State Acts dataset (24+ provisions)
│       └── court_judgments.json   ← Landmark SC judgments (12+)
│
├── legal_database/
│   ├── schema.sql                 ← PostgreSQL schema
│   └── store.py                  ← Database store (insert/update/search)
│
├── retrieval_engine/
│   └── embedding_generator.py    ← ChromaDB embedding pipeline
│
├── scheduler/
│   └── update_scheduler.py       ← Automatic update scheduler
│
└── requirements.txt
```

---

## Prerequisites

### 1. Install Python 3.10+

```bash
python --version  # Should be 3.10 or higher
```

### 2. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For dynamic page crawling (JS-rendered court portals):
```bash
pip install playwright
playwright install chromium
```

For Celery distributed scheduler (optional):
```bash
pip install celery redis
```

---

## Quick Start — Run Everything in VS Code

### Step 1: Open Terminal in VS Code
`Ctrl+`` ` (backtick) to open integrated terminal

### Step 2: Navigate to backend
```bash
cd backend
```

### Step 3: Generate all datasets (offline mode — no internet needed)

```bash
# Set encoding for Windows
set PYTHONIOENCODING=utf-8

# Constitution of India
python -m data_pipeline.crawler_constitution --offline --export data_pipeline/datasets/constitution.json

# Central Acts (BNS, IPC, IT Act, Consumer Protection, etc.)
python -m data_pipeline.crawler_central_laws --offline --export data_pipeline/datasets/laws.json

# State Acts (10 states)
python -m data_pipeline.crawler_state_laws --offline --export data_pipeline/datasets/state_laws.json

# Landmark SC Judgments
python -m data_pipeline.crawler_court_judgments --offline --export data_pipeline/datasets/court_judgments.json
```

### Step 4: Initialize database and load data

```bash
# Initialize DB (creates tables)
python -m legal_database.store init

# Import all generated datasets
python -m legal_database.store import data_pipeline/datasets/laws.json
python -m legal_database.store import data_pipeline/datasets/constitution.json
python -m legal_database.store import data_pipeline/datasets/state_laws.json
python -m legal_database.store import data_pipeline/datasets/court_judgments.json

# Check DB stats
python -m legal_database.store stats
```

### Step 5: Generate embeddings

```bash
# Index all laws into ChromaDB
python -m retrieval_engine.embedding_generator index

# Test semantic search
python -m retrieval_engine.embedding_generator search "someone stole my phone"
python -m retrieval_engine.embedding_generator search "fundamental rights violation"
```

---

## Crawler Modules — Detailed Usage

### Constitution Crawler

```bash
# Offline (seed data — fast)
python -m data_pipeline.crawler_constitution --offline --export constitution.json

# Live crawl (india.gov.in)
python -m data_pipeline.crawler_constitution --export constitution.json

# Slow down requests (be polite)
python -m data_pipeline.crawler_constitution --delay 3.0 --export constitution.json
```

**Extracts:** Articles 12–395+, Schedules 1–12, Amendments 1–106

---

### Central Laws Crawler

```bash
# Offline seed data (BNS, BNSS, IT Act, Consumer Protection, etc.)
python -m data_pipeline.crawler_central_laws --offline --export laws.json

# Live crawl — specific acts
python -m data_pipeline.crawler_central_laws --act "BNS" "consumer" --export laws.json

# Live crawl — limit to 5 acts (for testing)
python -m data_pipeline.crawler_central_laws --limit 5 --export laws.json

# Full crawl — all 20 priority acts
python -m data_pipeline.crawler_central_laws --export laws.json
```

**Priority Acts Covered:**
- Bharatiya Nyaya Sanhita, 2023 (BNS) — replaces IPC
- Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) — replaces CrPC
- Bharatiya Sakshya Adhiniyam, 2023 (BSA) — replaces Evidence Act
- Indian Penal Code, 1860 (IPC)
- Information Technology Act, 2000
- Consumer Protection Act, 2019
- Motor Vehicles Act, 1988
- POCSO Act, 2012
- RTI Act, 2005
- + 11 more

---

### State Laws Crawler

```bash
# Offline seed data (10 states)
python -m data_pipeline.crawler_state_laws --offline --export state_laws.json

# Specific states
python -m data_pipeline.crawler_state_laws --states Maharashtra Karnataka --export state_laws.json

# Skip eGazette (faster)
python -m data_pipeline.crawler_state_laws --no-gazette --export state_laws.json

# Live crawl all states
python -m data_pipeline.crawler_state_laws --export state_laws.json
```

**States Covered:** Maharashtra, Karnataka, Tamil Nadu, Kerala, Gujarat, Rajasthan, Uttar Pradesh, Delhi, West Bengal, Telangana, Andhra Pradesh, Madhya Pradesh, Punjab, Haryana

---

### Court Judgment Crawler

```bash
# Offline — 12 landmark Supreme Court judgments
python -m data_pipeline.crawler_court_judgments --offline --export court_judgments.json

# Supreme Court only
python -m data_pipeline.crawler_court_judgments --court supreme --export court_judgments.json

# Specific date range
python -m data_pipeline.crawler_court_judgments --from-date 01-01-2024 --to-date 31-12-2024

# With Playwright (for JS-rendered portals)
pip install playwright && playwright install chromium
python -m data_pipeline.crawler_court_judgments --dynamic --export court_judgments.json
```

**Landmark Judgments Included (seed data):**
- Maneka Gandhi v. Union of India (1978) — Article 21, right to life
- Kesavananda Bharati (1973) — Basic structure doctrine
- Vishaka v. State of Rajasthan (1997) — Sexual harassment guidelines
- Shreya Singhal v. Union of India (2015) — Section 66A struck down
- D.K. Basu v. State of West Bengal (1997) — Custodial torture
- Navtej Singh Johar (2018) — Section 377 decriminalized
- Justice K.S. Puttaswamy (2017) — Right to privacy
- Arnesh Kumar (2014) — Arrest guidelines
- Indira Sawhney (1992) — OBC reservation, 50% cap
- + 3 more

---

## Automatic Scheduler

The scheduler runs crawlers automatically on a cron schedule.

### Option A: APScheduler (Recommended)

```bash
# Install
pip install apscheduler

# Start scheduler (runs continuously)
python -m scheduler.update_scheduler

# One-shot run (all sources)
python -m scheduler.update_scheduler --run-now

# One-shot — specific source
python -m scheduler.update_scheduler --run-now --source judgments

# One-shot — offline
python -m scheduler.update_scheduler --run-now --offline

# Check run history
python -m scheduler.update_scheduler --status
```

**Default Schedule:**
| Source | Schedule | Time |
|--------|----------|------|
| Constitution | Monthly | 1st of month, 4:00 AM IST |
| Central Acts | Weekly | Sunday, 3:00 AM IST |
| State Acts | Weekly | Sunday, 4:00 AM IST |
| Judgments | Daily | 2:00 AM IST |

### Customizing Schedule (environment variables)

```bash
# Windows
set SCHEDULE_JUDGMENTS=0 6 * * *     # 6 AM daily
set SCHEDULE_LAWS=0 2 * * 1          # 2 AM Monday
set CRAWL_DELAY=3.0                  # 3 second delay between requests

# Linux/macOS
export SCHEDULE_JUDGMENTS="0 6 * * *"
export CRAWL_DELAY=3.0
```

### Option B: Celery (Distributed — Production)

```bash
# Install
pip install celery redis

# Start Redis (required)
docker run -d -p 6379:6379 redis

# Start Celery worker
celery -A scheduler.update_scheduler.celery_app worker --loglevel=info

# Start Celery beat (scheduler)
celery -A scheduler.update_scheduler.celery_app beat --loglevel=info
```

### Option C: Simple Scheduler (No Dependencies)

```bash
python -m scheduler.update_scheduler --mode simple
```

---

## Database Setup

### SQLite (Development — default)

SQLite is auto-created at `backend/yama_ai.db`. No setup needed.

```bash
python -m legal_database.store init
```

### PostgreSQL (Production)

1. Create database:
```sql
CREATE DATABASE yama_ai;
```

2. Apply schema:
```bash
psql -U postgres -d yama_ai -f legal_database/schema.sql
```

3. Set environment variable:
```bash
# Windows
set DATABASE_URL=postgresql://postgres:password@localhost:5432/yama_ai

# Linux/macOS
export DATABASE_URL=postgresql://postgres:password@localhost:5432/yama_ai
```

4. Initialize:
```bash
python -m legal_database.store init
```

---

## Embedding + Vector Search

```bash
# Index all laws (generates embeddings, stores in ChromaDB)
python -m retrieval_engine.embedding_generator index

# Semantic search
python -m retrieval_engine.embedding_generator search "theft of motorcycle"
python -m retrieval_engine.embedding_generator search "arrest without warrant"
python -m retrieval_engine.embedding_generator search "fundamental right to privacy"

# View collection stats
python -m retrieval_engine.embedding_generator stats

# Full re-index (drop + re-create)
python -m retrieval_engine.embedding_generator reindex
```

### Embedding Models

| Model | Dimensions | Speed | Quality |
|-------|-----------|-------|---------|
| all-MiniLM-L6-v2 (default) | 384 | Fast | Good |
| all-mpnet-base-v2 | 768 | Slow | Best |
| legal-bert-base-uncased | 768 | Slow | Legal domain |

```bash
# Set model via environment variable
set EMBEDDING_MODEL=all-mpnet-base-v2
python -m retrieval_engine.embedding_generator index
```

---

## Data Schema

### Central Acts / State Acts / Constitution JSON

```json
{
  "act_name": "Bharatiya Nyaya Sanhita, 2023",
  "section_number": "303",
  "title": "Theft",
  "description": "Whoever, intending to take dishonestly...",
  "keywords": "theft, dishonest, moveable, property",
  "jurisdiction": "central",
  "state_name": null,
  "law_type": "act",
  "category": "criminal",
  "punishment": "Imprisonment up to 3 years, or fine, or both.",
  "old_law_reference": "Indian Penal Code, 1860, Section 378",
  "source_url": "https://www.indiacode.nic.in/...",
  "content_hash": "sha256...",
  "last_updated": "2024-01-01T00:00:00+00:00"
}
```

### Court Judgments JSON

```json
{
  "case_name": "Maneka Gandhi v. Union of India",
  "court": "Supreme Court of India",
  "date": "1978-01-25",
  "citation": "AIR 1978 SC 597",
  "bench": "M.H. Beg CJ, ...",
  "legal_topic": "fundamental_rights, constitutional",
  "summary": "The Supreme Court expanded the scope of Article 21...",
  "acts_cited": ["Constitution of India, Article 21"],
  "legal_principles": ["Right to life includes right to live with human dignity"],
  "keywords": "article21, liberty, passport, procedure",
  "source_url": "https://main.sci.gov.in/...",
  "last_updated": "2024-01-01T00:00:00+00:00"
}
```

### PostgreSQL Tables

| Table | Description |
|-------|-------------|
| `laws` | All legal provisions (acts, articles, rules, judgments) |
| `legal_categories` | Category lookup (criminal, civil, constitutional...) |
| `ingestion_logs` | Audit trail of every crawl run |
| `chat_sessions` | User conversation sessions |
| `chat_messages` | Individual chat messages |

---

## Scalability Notes

| Scale | Configuration |
|-------|--------------|
| Dev | SQLite + Simple Scheduler + CPU embeddings |
| Staging | PostgreSQL + APScheduler + GPU embeddings |
| Production | PostgreSQL (RDS) + Celery + Redis + GPU server |

For millions of judgments:
- Partition `laws` table by year
- Add full-text search index (already in schema.sql)
- Use dedicated ChromaDB server (Docker)
- Use Celery with multiple workers

---

## VS Code Tasks (Optional)

Add to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Generate All Datasets",
      "type": "shell",
      "command": "cd backend && set PYTHONIOENCODING=utf-8 && python -m data_pipeline.crawler_constitution --offline --export data_pipeline/datasets/constitution.json && python -m data_pipeline.crawler_central_laws --offline --export data_pipeline/datasets/laws.json && python -m data_pipeline.crawler_state_laws --offline --export data_pipeline/datasets/state_laws.json && python -m data_pipeline.crawler_court_judgments --offline --export data_pipeline/datasets/court_judgments.json",
      "group": "build"
    },
    {
      "label": "Start Scheduler",
      "type": "shell",
      "command": "cd backend && python -m scheduler.update_scheduler",
      "group": "build",
      "isBackground": true
    },
    {
      "label": "Run Full Ingestion (Offline)",
      "type": "shell",
      "command": "cd backend && python -m scheduler.update_scheduler --run-now --offline",
      "group": "build"
    }
  ]
}
```

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'requests'` | Run `pip install -r requirements.txt` |
| `UnicodeEncodeError` on Windows | Run `set PYTHONIOENCODING=utf-8` before any command |
| `HTTP 403 / 429` from court portals | Increase delay: `--delay 5.0` |
| `chromadb` import error | Run `pip install chromadb` |
| `apscheduler` not found | Run `pip install apscheduler` |
| SQLite locked | Stop other processes using the DB |
| Empty live crawl results | Court/legislation portals may be down — use `--offline` |

---

## Data Sources

| Source | URL | Data |
|--------|-----|------|
| India Code | https://www.indiacode.nic.in | All Central Acts |
| Legislative Dept | https://legislative.gov.in | Bills, Ordinances |
| eGazette | https://egazette.gov.in | Notifications, Rules |
| Supreme Court | https://main.sci.gov.in | SC Judgments |
| eCourts | https://services.ecourts.gov.in | HC/District Court |
| india.gov.in | https://www.india.gov.in | Constitution |
| State portals | Various | State Acts |

All sources are **official government websites only**.
