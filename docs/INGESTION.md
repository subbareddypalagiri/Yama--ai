# YAMA AI — Legal Knowledge Ingestion System

## Overview

The ingestion system automatically collects, cleans, structures, and stores Indian legal data from official government sources. It feeds the YAMA AI legal analysis engine with up-to-date provisions from central acts, state laws, constitutional articles, court judgments, and gazette notifications.

## Architecture

```
Internet Sources ─────────────────────────────────────────┐
│  India Code  │  Constitution  │  SCI  │  eGazette  │  State Portals  │
└──────────────┴────────────────┴───────┴────────────┴─────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │    Crawlers         │  (india_code, constitution,
                    │    (base_crawler)   │   court, gazette, state)
                    └─────────┬──────────┘
                              │ List[LegalRecord]
                    ┌─────────▼──────────┐
                    │  Text Extractor    │  Parse HTML → sections
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Data Cleaner      │  Normalize, validate, deduplicate
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Metadata Tagger   │  Auto-classify, tag jurisdiction,
                    │                    │  map old↔new laws (IPC↔BNS)
                    └─────────┬──────────┘
                              │ List[dict]
                    ┌─────────▼──────────┐
                    │  Storage Pipeline  │
                    │  ┌───────┐ ┌─────┐ │
                    │  │SQLite │ │Chroma│ │  Upsert + content-hash dedup
                    │  │/PgSQL │ │  DB  │ │  + embedding generation
                    │  └───────┘ └─────┘ │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Exporter          │  JSON / CSV / SQL / JSONL
                    └────────────────────┘
```

## Project Structure

```
backend/ingestion/
├── __init__.py              # Package init
├── __main__.py              # CLI runner (python -m ingestion)
├── config.py                # Source registry, settings, state list
├── crawlers/
│   ├── __init__.py
│   ├── base_crawler.py      # Abstract base: HTTP, retry, rate-limit
│   ├── india_code_crawler.py    # India Code central legislation
│   ├── constitution_crawler.py  # Constitution of India
│   ├── court_crawler.py         # Supreme Court + High Court judgments
│   └── gazette_crawler.py       # eGazette + State law portals
├── text_extractor.py        # HTML/text → structured sections
├── data_cleaner.py          # Clean, normalize, validate, deduplicate
├── metadata_tagger.py       # Auto-classify, tag, map old↔new laws
├── storage_pipeline.py      # SQLite/PgSQL + ChromaDB upsert
├── exporter.py              # Export to JSON, CSV, SQL, JSONL
├── scheduler.py             # Background task scheduler
├── datasets/
│   └── example_laws.json    # 92 curated Indian legal provisions
└── export/                  # Generated export files
    ├── yama_ai_laws.json
    ├── yama_ai_laws.csv
    ├── yama_ai_laws.sql
    └── yama_ai_laws_embeddings.jsonl
```

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Load the Example Dataset

```bash
cd backend
python -m ingestion load --file ingestion/datasets/example_laws.json
```

This will:
1. Read 92 legal provisions from the JSON file
2. Clean and validate each record
3. Auto-tag with category, jurisdiction, law type
4. Store in SQLite database
5. Generate embeddings and index into ChromaDB

### Export Data

```bash
# Export all formats (JSON, CSV, SQL, JSONL)
python -m ingestion export --format all

# Export specific format
python -m ingestion export --format json
python -m ingestion export --format csv
python -m ingestion export --format sql
python -m ingestion export --format embeddings
```

### Run a Crawler

```bash
# Crawl a specific source
python -m ingestion run --source india_code
python -m ingestion run --source constitution
python -m ingestion run --source supreme_court

# Crawl all sources
python -m ingestion run --all
```

### Show Available Sources

```bash
python -m ingestion info
```

### Start Background Scheduler

```bash
python -m ingestion scheduler --status   # View task schedule
python -m ingestion scheduler --start    # Start background scheduler
```

## API Endpoints

Start the server first:

```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Then use the ingestion API:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/ingestion/stats` | Database statistics (counts by category, jurisdiction, etc.) |
| GET | `/api/v1/ingestion/status` | Ingestion run history (last 20 runs) |
| POST | `/api/v1/ingestion/load` | Load records via JSON body |
| POST | `/api/v1/ingestion/load-file` | Upload a JSON file |
| POST | `/api/v1/ingestion/crawl` | Trigger a crawler |
| POST | `/api/v1/ingestion/export` | Export data to files |

### Example: Load via API

```bash
curl -X POST http://localhost:8000/api/v1/ingestion/load \
  -H "Content-Type: application/json" \
  -d '{
    "laws": [{
      "act_name": "Indian Contract Act, 1872",
      "section_number": "10",
      "title": "What agreements are contracts",
      "description": "All agreements are contracts if made by free consent...",
      "keywords": "contract, agreement",
      "category": "civil",
      "jurisdiction": "central",
      "law_type": "act"
    }],
    "source_name": "manual"
  }'
```

### Example: Get Stats

```bash
curl http://localhost:8000/api/v1/ingestion/stats
```

## Data Record Format

Every legal record follows this structure:

```json
{
  "act_name": "Bharatiya Nyaya Sanhita, 2023",
  "section_number": "303",
  "title": "Theft",
  "description": "Whoever, intending to take dishonestly any moveable property...",
  "keywords": "theft, stealing, dishonest taking, moveable property",
  "category": "criminal",
  "punishment": "Imprisonment up to three years, or fine, or both.",
  "old_law_reference": "Indian Penal Code, Section 378",
  "jurisdiction": "central",
  "state_name": null,
  "law_type": "act",
  "source_url": "https://www.indiacode.nic.in/...",
  "content_hash": "a1b2c3..."
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `act_name` | string | Full name of the act/law |
| `section_number` | string | Section, Article, or Rule number |
| `title` | string | Marginal heading / title |
| `description` | string | Full text of the provision |
| `keywords` | string | Comma-separated keywords |
| `category` | string | criminal, civil, constitutional, consumer, cyber, family, motor_vehicle, labour, property, tax, environmental, corporate |
| `punishment` | string? | Penalty/punishment if applicable |
| `old_law_reference` | string? | Equivalent provision in old law (IPC→BNS mapping) |
| `jurisdiction` | string | "central" or "state" |
| `state_name` | string? | State name if state-level law |
| `law_type` | string | act, rule, article, amendment, judgment, notification, ordinance |
| `source_url` | string? | URL of the official source |
| `content_hash` | string | SHA-256 for change detection |

## Pipeline Modules

### Crawlers

Each crawler extends `BaseCrawler` which provides:
- HTTP client with polite request delays (2s between requests)
- Automatic retry with exponential backoff
- Rate limiting (respects 429/503)
- Stats tracking

Available crawlers:
- **IndiaCodeCrawler** — Central acts from indiacode.nic.in
- **ConstitutionCrawler** — Constitutional articles
- **SupremeCourtCrawler** — SCI judgments
- **HighCourtCrawler** — High Court judgments
- **GazetteCrawler** — Government gazette notifications
- **StateLawCrawler** — State legislation portals

### Data Cleaner

- Removes HTML artifacts, encoding issues
- Normalizes section numbers ("Section 302" → "302")
- Standardizes act names (aliases: "IPC" → "Indian Penal Code, 1860")
- Validates required fields
- Deduplicates via content hash

### Metadata Tagger

- Auto-classifies into 12 legal categories using keyword matching
- Detects jurisdiction (central vs state) and state name
- Infers law type (act, rule, article, judgment, etc.)
- Maps old↔new laws (IPC↔BNS, CrPC↔BNSS, Evidence Act↔BSA)
- Auto-generates keywords from text

### Storage Pipeline

- Batch upserts to SQLite/PostgreSQL
- Content-hash comparison skips unchanged records
- Automatic ChromaDB embedding and indexing
- Transaction-safe with rollback on error
- Logs every run to `ingestion_logs` table

### Exporter

- **JSON** — Structured export with metadata header
- **CSV** — Spreadsheet-compatible
- **SQL** — INSERT statements with CREATE TABLE DDL
- **JSONL** — Embedding-ready (one doc per line)

## Scheduler

The built-in scheduler runs tasks on configurable intervals:

| Task | Default Interval |
|------|-----------------|
| India Code crawl | Weekly |
| Constitution update | Monthly |
| Court judgments | Daily |
| Gazette notifications | Daily |
| State laws | Weekly |

For production, use OS-level scheduling:

```bash
# Linux crontab
0 2 * * * cd /path/to/backend && python -m ingestion run --source supreme_court
0 3 * * 0 cd /path/to/backend && python -m ingestion run --source india_code

# Windows Task Scheduler
# Create task: python -m ingestion run --source supreme_court
```

## Current Dataset

The example dataset contains **92 provisions** from:

| Act | Sections |
|-----|----------|
| Bharatiya Nyaya Sanhita, 2023 (BNS) | 37 |
| Constitution of India | 10 |
| Information Technology Act, 2000 | 10 |
| Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) | 9 |
| Consumer Protection Act, 2019 | 6 |
| Motor Vehicles Act, 1988 | 5 |
| Protection of Women from Domestic Violence Act, 2005 | 4 |
| Bharatiya Sakshya Adhiniyam, 2023 (BSA) | 4 |
| Right to Information Act, 2005 | 4 |

## Adding New Data

### Method 1: JSON File

Create a JSON file with the standard format and load it:

```bash
python -m ingestion load --file path/to/your/data.json
```

### Method 2: API

POST to `/api/v1/ingestion/load` with a JSON body.

### Method 3: Custom Crawler

1. Create a new file in `ingestion/crawlers/`
2. Extend `BaseCrawler`
3. Implement `source_name` property and `crawl()` method
4. Register in `__main__.py` and `scheduler.py`
