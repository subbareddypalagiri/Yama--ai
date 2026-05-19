# YAMA AI — System Architecture Document

> **Version**: 1.0.0
> **Last Updated**: 2026-03-15
> **Status**: Production Design — Fully Implemented

---

## Table of Contents

1. [High-Level System Overview](#1-high-level-system-overview)
2. [Complete Project Folder Structure](#2-complete-project-folder-structure)
3. [Module-by-Module Explanation](#3-module-by-module-explanation)
4. [Component Interaction Map](#4-component-interaction-map)
5. [Data Flow Pipeline](#5-data-flow-pipeline)
6. [Database Architecture](#6-database-architecture)
7. [API Contract](#7-api-contract)
8. [AI Reasoning Engine Design](#8-ai-reasoning-engine-design)
9. [RAG Retrieval Pipeline Design](#9-rag-retrieval-pipeline-design)
10. [Security & Guardrails](#10-security--guardrails)

---

## 1. High-Level System Overview

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         YAMA AI — SYSTEM ARCHITECTURE                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   ┌────────────────────────────────────────────────────────────────────┐     ║
║   │                     PRESENTATION LAYER                              │     ║
║   │                                                                      │     ║
║   │   Next.js 14 + TailwindCSS + TypeScript                            │     ║
║   │                                                                      │     ║
║   │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │     ║
║   │   │  Landing  │  │   Chat   │  │  Search  │  │ Explorer │          │     ║
║   │   │  Page     │  │Interface │  │  Laws    │  │  Acts    │          │     ║
║   │   └──────────┘  └──────────┘  └──────────┘  └──────────┘          │     ║
║   └────────────────────────┬───────────────────────────────────────────┘     ║
║                            │ HTTP (JSON) via Next.js Rewrite Proxy           ║
║                            ▼                                                  ║
║   ┌────────────────────────────────────────────────────────────────────┐     ║
║   │                       API GATEWAY LAYER                             │     ║
║   │                                                                      │     ║
║   │   FastAPI + Uvicorn (Python 3.11+)                                  │     ║
║   │                                                                      │     ║
║   │   ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐         │     ║
║   │   │ /api/v1/  │ │ /api/v1/  │ │ /api/v1/  │ │ /api/v1/  │         │     ║
║   │   │  chat     │ │  laws     │ │  analyze  │ │  health   │         │     ║
║   │   └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └───────────┘         │     ║
║   └─────────┼─────────────┼─────────────┼──────────────────────────────┘     ║
║             │             │             │                                      ║
║             ▼             ▼             ▼                                      ║
║   ┌────────────────────────────────────────────────────────────────────┐     ║
║   │                    SERVICE / INTELLIGENCE LAYER                      │     ║
║   │                                                                      │     ║
║   │   ┌──────────────────────┐    ┌──────────────────────┐              │     ║
║   │   │   RAG Pipeline       │    │   IRAC Reasoning     │              │     ║
║   │   │   (rag_pipeline.py)  │───▶│   Engine             │              │     ║
║   │   │                      │    │   (reasoning.py)     │              │     ║
║   │   │ • Retrieve laws      │    │                      │              │     ║
║   │   │ • Merge & rank       │    │ • Fact extraction    │              │     ║
║   │   │ • Format for LLM     │    │ • Issue → Rule →     │              │     ║
║   │   └───────┬──────┬───────┘    │   Application →      │              │     ║
║   │           │      │            │   Conclusion         │              │     ║
║   │           │      │            └──────────┬───────────┘              │     ║
║   │           │      │                       │                          │     ║
║   └───────────┼──────┼───────────────────────┼──────────────────────────┘     ║
║               │      │                       │                                ║
║               ▼      ▼                       ▼                                ║
║   ┌────────────────────────┐    ┌────────────────────────┐                   ║
║   │    DATA LAYER          │    │    EXTERNAL AI LAYER    │                   ║
║   │                        │    │                        │                   ║
║   │  ┌──────────────────┐  │    │  ┌──────────────────┐  │                   ║
║   │  │   PostgreSQL 16   │  │    │  │  LLM Provider    │  │                   ║
║   │  │                  │  │    │  │  (llm_provider.py)│  │                   ║
║   │  │ • law_sections   │  │    │  │                  │  │                   ║
║   │  │ • legal_categories│  │    │  │  OpenAI GPT-4   │  │                   ║
║   │  │ • chat_sessions  │  │    │  │  Claude Sonnet   │  │                   ║
║   │  │ • chat_messages  │  │    │  │  Ollama/Mistral  │  │                   ║
║   │  └──────────────────┘  │    │  └──────────────────┘  │                   ║
║   │                        │    │                        │                   ║
║   │  ┌──────────────────┐  │    └────────────────────────┘                   ║
║   │  │   ChromaDB        │  │                                                ║
║   │  │   (Vector Store)  │  │                                                ║
║   │  │                  │  │                                                ║
║   │  │ • Cosine HNSW    │  │                                                ║
║   │  │ • Embeddings of  │  │                                                ║
║   │  │   all law texts  │  │                                                ║
║   │  └──────────────────┘  │                                                ║
║   └────────────────────────┘                                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

The system is organized into **four horizontal layers**, each with a clear responsibility boundary:

| Layer | Responsibility | Technology |
|-------|---------------|-----------|
| **Presentation** | User interface, user input capture, response rendering | Next.js 14, TailwindCSS, TypeScript |
| **API Gateway** | Request validation, routing, session management, response formatting | FastAPI, Pydantic, SQLAlchemy |
| **Service / Intelligence** | Law retrieval, IRAC reasoning, RAG orchestration | LangChain, ChromaDB client, custom Python |
| **Data** | Persistent storage of laws, sessions, and vector embeddings | PostgreSQL 16, ChromaDB |
| **External AI** | Large language model inference | OpenAI / Anthropic / Ollama (configurable) |

---

## 2. Complete Project Folder Structure

```
yama-ai/
│
├── .gitignore                          # Git ignore rules
├── docker-compose.yml                  # Full-stack container orchestration
├── README.md                           # Project overview and quick start
│
├── docs/
│   └── ARCHITECTURE.md                 # ← This file
│
├── backend/                            # ════ PYTHON FASTAPI SERVER ════
│   ├── .env.example                    # Environment variable template
│   ├── Dockerfile                      # Backend container image
│   ├── requirements.txt                # Python dependencies (pinned)
│   ├── main.py                         # FastAPI app entry point
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── core/                       # ── App-wide configuration ──
│   │   │   ├── __init__.py             # Re-exports settings, constants
│   │   │   ├── config.py              # Pydantic Settings (env → typed config)
│   │   │   └── constants.py           # Legal categories, IRAC prompt, disclaimer
│   │   │
│   │   ├── db/                         # ── Database layer ──
│   │   │   ├── __init__.py
│   │   │   ├── database.py            # SQLAlchemy engine + session factory
│   │   │   ├── models.py             # ORM models (4 tables)
│   │   │   └── init_db.py            # Table creation + seed data (30+ laws)
│   │   │
│   │   ├── models/                     # ── Request / Response schemas ──
│   │   │   ├── __init__.py
│   │   │   └── schemas.py            # Pydantic models for API contracts
│   │   │
│   │   ├── api/                        # ── HTTP API surface ──
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── chat.py            # POST /chat — situation analysis
│   │   │       ├── laws.py            # GET  /laws/* — search, browse, explore
│   │   │       ├── analyze.py         # POST /analyze — deep IRAC analysis
│   │   │       └── health.py          # GET  /health — system status
│   │   │
│   │   └── services/                   # ── Business logic ──
│   │       ├── __init__.py
│   │       │
│   │       ├── ai_engine/             # ── AI Reasoning Layer ──
│   │       │   ├── __init__.py
│   │       │   ├── llm_provider.py    # LLM factory (OpenAI/Anthropic/Ollama)
│   │       │   └── reasoning.py       # IRACReasoningEngine class
│   │       │
│   │       └── retrieval_engine/      # ── RAG Retrieval Layer ──
│   │           ├── __init__.py
│   │           ├── vector_store.py    # ChromaDB wrapper (LegalVectorStore)
│   │           ├── rag_pipeline.py    # RAGPipeline orchestrator
│   │           └── indexer.py         # Bulk index laws into ChromaDB
│   │
│   └── legal_database/
│       └── seeds/                      # (Reserved for CSV/JSON seed files)
│
└── frontend/                           # ════ NEXT.JS APPLICATION ════
    ├── Dockerfile                      # Frontend container image
    ├── package.json                    # Node dependencies
    ├── tsconfig.json                   # TypeScript configuration
    ├── next.config.js                  # Next.js config + API proxy rewrite
    ├── tailwind.config.js              # TailwindCSS theme (justice colors)
    ├── postcss.config.js               # PostCSS pipeline
    │
    ├── public/                         # Static assets
    │
    └── src/
        ├── app/                        # ── Next.js App Router Pages ──
        │   ├── globals.css            # Global styles + markdown analysis CSS
        │   ├── layout.tsx             # Root HTML layout with metadata
        │   ├── page.tsx               # Landing page (hero, features, IRAC)
        │   │
        │   ├── chat/
        │   │   └── page.tsx           # Chat interface (core UX)
        │   │
        │   ├── search/
        │   │   └── page.tsx           # Law search with category filters
        │   │
        │   └── explore/
        │       └── page.tsx           # Act/section browser (sidebar + detail)
        │
        ├── components/                 # ── Reusable React components ──
        │   ├── chat/                  # (Chat-specific components)
        │   ├── layout/                # (Header, footer, navigation)
        │   └── ui/                    # (Shared UI primitives)
        │
        ├── lib/
        │   └── api.ts                 # API client (7 typed fetch functions)
        │
        └── types/
            └── index.ts               # TypeScript interfaces (shared types)
```

**Total files**: 45
**Backend files**: 27 (Python)
**Frontend files**: 14 (TypeScript/CSS/Config)
**Root config**: 4 (docker-compose, .gitignore, README, architecture doc)

---

## 3. Module-by-Module Explanation

### 3.1 — `backend/main.py` — Application Entry Point

| Aspect | Detail |
|--------|--------|
| **Role** | Creates the FastAPI application instance and wires everything together |
| **What it does** | 1) Instantiates `FastAPI` with metadata. 2) Attaches CORS middleware (origins from `.env`). 3) Registers all four route modules under `/api/v1`. 4) Exposes a root `/` endpoint with system info. |
| **Runs via** | `uvicorn main:app --reload --port 8000` |

---

### 3.2 — `backend/app/core/` — Configuration & Constants

#### `config.py`
| Aspect | Detail |
|--------|--------|
| **Role** | Single source of truth for all environment-driven settings |
| **Pattern** | Uses `pydantic-settings.BaseSettings` — reads `.env` file automatically |
| **Key settings** | `DATABASE_URL`, `LLM_PROVIDER` (openai/anthropic/ollama), API keys, `CHROMA_PERSIST_DIR`, `CORS_ORIGINS` |
| **Exported as** | Singleton `settings` object imported everywhere |

#### `constants.py`
| Aspect | Detail |
|--------|--------|
| **Role** | Hardcoded legal domain knowledge that does not change per-environment |
| **Contains** | `LEGAL_CATEGORIES` (10 categories), `SUPPORTED_ACTS` (16 acts), `IRAC_SYSTEM_PROMPT` (full LLM system prompt with output format rules), `SAFETY_DISCLAIMER` |
| **Why separate** | Prompt engineering is domain logic, not configuration — editing the prompt should not require touching env variables |

---

### 3.3 — `backend/app/db/` — Database Layer

#### `database.py`
| Aspect | Detail |
|--------|--------|
| **Role** | Creates SQLAlchemy `engine` and `SessionLocal` factory |
| **Pattern** | `get_db()` generator function used as a FastAPI dependency — provides a DB session per request and auto-closes it |
| **Connection** | `pool_pre_ping=True` for resilient reconnection |

#### `models.py` — ORM Models (4 Tables)
| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `law_sections` | Stores every section/provision of every supported Indian act | `act_name`, `section_number`, `title`, `description`, `keywords`, `category`, `punishment`, `old_law_reference`, `is_active` |
| `legal_categories` | Taxonomy for classifying laws | `name`, `slug`, `description` |
| `chat_sessions` | Groups messages into conversations | `session_id` (UUID) |
| `chat_messages` | Individual user/assistant messages | `session_id` (FK), `role`, `content` |

**Indexes**: `act_name`, `category`, composite unique on `(act_name, section_number)`, `session_id`.

#### `init_db.py`
| Aspect | Detail |
|--------|--------|
| **Role** | Idempotent database bootstrapper — creates tables and seeds data |
| **Seed data** | 30+ legal provisions from 9 acts: BNS, BNSS, BSA, Constitution, IT Act, Consumer Protection Act, Motor Vehicles Act, DV Act, RTI Act |
| **Run via** | `python -m app.db.init_db` |
| **Idempotent** | Checks for existing records before inserting — safe to re-run |

---

### 3.4 — `backend/app/models/schemas.py` — API Contracts

Defines all Pydantic models used for request validation and response serialization:

| Model | Direction | Used By |
|-------|-----------|---------|
| `ChatRequest` | Request | `POST /chat` |
| `AnalyzeRequest` | Request | `POST /analyze` |
| `LawSearchRequest` | Request | (Internal use) |
| `LawSectionResponse` | Response | All endpoints returning law data |
| `LegalAnalysis` | Response | `POST /analyze` — structured IRAC output |
| `ChatResponse` | Response | `POST /chat` — markdown analysis + sections |
| `SearchResponse` | Response | `GET /laws/search` |
| `HealthResponse` | Response | `GET /health` |

**Validation**: `ChatRequest.message` requires 10–5000 chars. `AnalyzeRequest.situation` requires 20–10000 chars.

---

### 3.5 — `backend/app/api/routes/` — API Endpoints

#### `chat.py` — `/api/v1/chat`
| Aspect | Detail |
|--------|--------|
| **Method** | `POST` |
| **Input** | `{ message: string, session_id?: string }` |
| **Output** | `{ session_id, analysis (markdown), relevant_sections[], timestamp }` |
| **Flow** | Create/resume session → Save user message → Run RAG pipeline → Save assistant response → Return |

#### `laws.py` — `/api/v1/laws/*`
| Endpoint | Method | What It Does |
|----------|--------|-------------|
| `/laws/search?q=...&category=...&limit=...` | GET | Hybrid search (vector + keyword) |
| `/laws/sections/{act_name}` | GET | All sections of an act, ordered by section number |
| `/laws/categories` | GET | All 10 legal categories |
| `/laws/acts` | GET | Distinct act names from DB |
| `/laws/{law_id}` | GET | Single section by primary key |

#### `analyze.py` — `/api/v1/analyze`
| Aspect | Detail |
|--------|--------|
| **Method** | `POST` |
| **Input** | `{ situation: string, category?: string }` |
| **Output** | Structured `LegalAnalysis` with individual fields parsed from the markdown |
| **Special logic** | Uses regex to extract IRAC sections from the LLM's markdown output into discrete fields (`fact_summary`, `legal_questions[]`, etc.) |

#### `health.py` — `/api/v1/health`
| Aspect | Detail |
|--------|--------|
| **Method** | `GET` |
| **Checks** | PostgreSQL connectivity (`SELECT 1`), ChromaDB document count |
| **Output** | `{ status: "healthy"|"degraded", version, database, vector_store }` |

---

### 3.6 — `backend/app/services/ai_engine/` — AI Reasoning

#### `llm_provider.py`
| Aspect | Detail |
|--------|--------|
| **Role** | Factory function that returns the configured LLM |
| **Pattern** | Reads `settings.LLM_PROVIDER` and instantiates the matching LangChain chat model |
| **Supported** | `ChatOpenAI` (GPT-4), `ChatAnthropic` (Claude), `ChatOllama` (Mistral/LLaMA) |
| **Temperature** | Fixed at `0.3` — low creativity, high factual accuracy |
| **Max tokens** | 4000 — sufficient for comprehensive IRAC analysis |

#### `reasoning.py` — `IRACReasoningEngine`
| Method | Purpose |
|--------|---------|
| `analyze(situation, retrieved_laws)` | **Primary method.** Takes user situation + retrieved law text → Sends to LLM with IRAC system prompt → Returns full markdown analysis |
| `extract_facts(situation)` | Extracts objective bullet-point facts (auxiliary) |
| `classify_issues(situation)` | Classifies legal domains involved (auxiliary) |

**Pattern**: Singleton via `get_reasoning_engine()`. Prompt uses LangChain `ChatPromptTemplate` with a system message (IRAC rules + output format) and a human message (situation + retrieved laws).

---

### 3.7 — `backend/app/services/retrieval_engine/` — RAG Pipeline

#### `vector_store.py` — `LegalVectorStore`
| Method | Purpose |
|--------|---------|
| `add_law(law_id, text, metadata)` | Insert one document |
| `add_laws_batch(laws)` | Bulk upsert |
| `search(query, n_results, category)` | Cosine similarity search with optional category filter |
| `get_count()` | Total indexed documents |

**Config**: ChromaDB with DuckDB+Parquet backend, HNSW cosine distance, persisted to `CHROMA_PERSIST_DIR`.

#### `rag_pipeline.py` — `RAGPipeline`
| Aspect | Detail |
|--------|--------|
| **Role** | Central orchestrator — the single class that wires retrieval to reasoning |
| **Dual retrieval** | Runs vector search (ChromaDB) AND keyword search (PostgreSQL) in parallel |
| **Merge logic** | Vector results first (better semantic quality), then SQL results deduplicated by ID |
| **Key method** | `analyze_situation(situation, category)` — full pipeline, returns `{ analysis, relevant_laws, retrieved_count }` |

#### `indexer.py`
| Aspect | Detail |
|--------|--------|
| **Role** | Reads all active `LawSection` rows from PostgreSQL and indexes them into ChromaDB |
| **Text format** | Concatenates: act name, section, title, description, keywords, punishment, old law reference |
| **Run via** | `python -m app.services.retrieval_engine.indexer` |

---

### 3.8 — `frontend/src/app/` — Next.js Pages

#### `page.tsx` — Landing Page (`/`)
| Section | Content |
|---------|---------|
| Hero | Title, description, "Start Legal Analysis" CTA button |
| Features | 3 cards: Situation Analyzer, Law Search, Section Explorer |
| IRAC Visualizer | 4 cards showing I → R → A → C with descriptions |
| Disclaimer | Legal disclaimer banner |
| Footer | Navigation links |

#### `chat/page.tsx` — Chat Interface (`/chat`)
| Aspect | Detail |
|--------|--------|
| **Role** | Primary user interaction surface |
| **Welcome state** | Shows 5 example situations as clickable buttons |
| **Input** | Auto-resizing textarea, Enter to send, Shift+Enter for newline |
| **Messages** | User messages in saffron bubbles (right), AI analysis in white cards (left) |
| **Markdown rendering** | `react-markdown` renders the IRAC analysis with styled headings, tables, lists |
| **Section tags** | Shows referenced law sections as small badges below each analysis |
| **State** | `session_id` maintained across messages for context |

#### `search/page.tsx` — Law Search (`/search`)
| Aspect | Detail |
|--------|--------|
| **Input** | Keyword text field + category dropdown (8 options) |
| **Results** | Cards with section badges, expandable descriptions, punishment tags |

#### `explore/page.tsx` — Section Explorer (`/explore`)
| Aspect | Detail |
|--------|--------|
| **Layout** | Left sidebar lists acts, right panel shows sections |
| **Interaction** | Click act → loads sections → Click section → expands description + punishment |

---

### 3.9 — `frontend/src/lib/api.ts` — API Client

7 typed fetch functions mapping to backend routes:

| Function | Calls |
|----------|-------|
| `sendChatMessage(message, sessionId?)` | `POST /api/v1/chat/` |
| `searchLaws(query, category?, limit?)` | `GET /api/v1/laws/search` |
| `getSectionsByAct(actName)` | `GET /api/v1/laws/sections/{act}` |
| `getLawById(id)` | `GET /api/v1/laws/{id}` |
| `getActs()` | `GET /api/v1/laws/acts` |
| `getCategories()` | `GET /api/v1/laws/categories` |
| `healthCheck()` | `GET /api/v1/health` |

**Proxy**: `next.config.js` rewrites `/api/*` to `http://localhost:8000/api/*` — frontend and backend share the same origin in development.

---

### 3.10 — `frontend/src/types/index.ts` — Shared Types

| Interface | Mirrors |
|-----------|---------|
| `ChatMessage` | Frontend-only (includes UI fields) |
| `LawSection` | `LawSectionResponse` from backend |
| `ChatApiResponse` | `ChatResponse` from backend |
| `SearchApiResponse` | `SearchResponse` from backend |

---

## 4. Component Interaction Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER (Browser)                                │
│                                                                         │
│  "My landlord refused to return my security deposit"                    │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  FRONTEND — Next.js (port 3000)                                         │
│                                                                         │
│  chat/page.tsx                                                          │
│    │                                                                    │
│    ├── handleSubmit()                                                   │
│    │     ├── Creates ChatMessage (role: "user")                         │
│    │     ├── Sets isLoading = true                                      │
│    │     └── Calls sendChatMessage() ──────────────────────┐            │
│    │                                                        │            │
│    └── On response:                                         │            │
│          ├── Creates ChatMessage (role: "assistant")         │            │
│          ├── Renders markdown via ReactMarkdown             │            │
│          └── Shows relevant section badges                  │            │
│                                                              │            │
│  lib/api.ts                                                  │            │
│    sendChatMessage(message, sessionId)                       │            │
│      └── fetch("POST /api/v1/chat/", {message, session_id}) │            │
└─────────────────────────────────────────────────────────────┼────────────┘
                                                               │
                         next.config.js rewrites               │
                         /api/* → http://localhost:8000/api/*   │
                                                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  BACKEND — FastAPI (port 8000)                                          │
│                                                                         │
│  main.py                                                                │
│    └── app.include_router(chat.router, prefix="/api/v1")                │
│                                                                         │
│  api/routes/chat.py                                                     │
│    chat_analyze(request, db)                                            │
│      ├── 1. Create/resume ChatSession (PostgreSQL)                      │
│      ├── 2. Save ChatMessage(role="user") → PostgreSQL                  │
│      ├── 3. pipeline = RAGPipeline(db) ─────────────────────┐           │
│      ├── 4. result = pipeline.analyze_situation(message)     │           │
│      ├── 5. Save ChatMessage(role="assistant") → PostgreSQL  │           │
│      └── 6. Return ChatResponse{analysis, relevant_sections} │           │
└──────────────────────────────────────────────────────────────┼───────────┘
                                                                │
                                                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  RAG PIPELINE — retrieval_engine/rag_pipeline.py                        │
│                                                                         │
│  RAGPipeline.analyze_situation(situation, category)                      │
│    │                                                                    │
│    ├── Step 1: retrieve_relevant_laws(situation)                        │
│    │     │                                                              │
│    │     ├── A. vector_store.search(situation)                          │
│    │     │     └── ChromaDB cosine similarity ── query ── "indian_laws" │
│    │     │         collection → top N matches with metadata             │
│    │     │                                                              │
│    │     ├── B. _keyword_search(situation)                              │
│    │     │     └── PostgreSQL: law_sections WHERE keywords/title/       │
│    │     │         description ILIKE '%term%' (OR across all terms)     │
│    │     │                                                              │
│    │     └── C. _merge_results(vector_results, sql_results)             │
│    │           └── Deduplicate by ID, vector results first              │
│    │                                                                    │
│    ├── Step 2: format_laws_for_prompt(relevant_laws)                    │
│    │     └── Converts law dicts → numbered text block for LLM           │
│    │                                                                    │
│    ├── Step 3: engine.analyze(situation, laws_text)                     │
│    │     │                                                              │
│    │     └── IRAC Reasoning Engine ─────────────────────────┐           │
│    │         (see Section 8 below)                            │           │
│    │                                                          │           │
│    └── Step 4: Return {analysis, relevant_laws, count}        │           │
└───────────────────────────────────────────────────────────────┼──────────┘
                                                                 │
                                                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  IRAC REASONING ENGINE — ai_engine/reasoning.py                         │
│                                                                         │
│  IRACReasoningEngine.analyze(situation, retrieved_laws)                  │
│    │                                                                    │
│    ├── Constructs ChatPromptTemplate:                                   │
│    │     ├── SystemMessage: IRAC_SYSTEM_PROMPT (constants.py)           │
│    │     │     • Core principles (never declare guilt)                  │
│    │     │     • IRAC framework definition                              │
│    │     │     • Exact output format (7 sections with emojis)           │
│    │     │     • Guidelines (simple language, cite sections)             │
│    │     │                                                              │
│    │     └── HumanMessage: situation + retrieved_laws                   │
│    │                                                                    │
│    ├── chain = prompt | self.llm                                        │
│    │                                                                    │
│    ├── response = chain.invoke({situation, retrieved_laws})              │
│    │     │                                                              │
│    │     └── LLM Call ──────────────────────────────────────────┐       │
│    │         llm_provider.py → get_llm()                         │       │
│    │         Based on LLM_PROVIDER env var:                      │       │
│    │           • "openai"    → ChatOpenAI(model="gpt-4")         │       │
│    │           • "anthropic" → ChatAnthropic(model="claude-3")   │       │
│    │           • "ollama"    → ChatOllama(model="mistral")       │       │
│    │         Temperature: 0.3 | Max tokens: 4000                 │       │
│    │                                                              │       │
│    └── return response.content (markdown string)                  │       │
└───────────────────────────────────────────────────────────────────┘       │
                                                                            │
                              ┌──────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  LLM OUTPUT (Markdown)                                                  │
│                                                                         │
│  ## ⚖️ FACT SUMMARY                                                     │
│  The user describes a situation where their landlord...                  │
│                                                                         │
│  ## 📋 LEGAL QUESTIONS                                                   │
│  1. Whether the landlord's retention of security deposit...             │
│  2. Whether this constitutes cheating under BNS Section 318...          │
│                                                                         │
│  ## 📖 RELEVANT LAWS                                                     │
│  | Act | Section | Title | Applicability |                              │
│  |-----|---------|-------|---------------|                              │
│  | ... | ...     | ...   | ...           |                              │
│                                                                         │
│  ## 🔍 LEGAL INTERPRETATION                                             │
│  ...                                                                    │
│                                                                         │
│  ## 📎 EVIDENCE COMMONLY REQUIRED                                        │
│  - Rental agreement / lease deed                                        │
│  - Payment receipts for security deposit                                │
│  ...                                                                    │
│                                                                         │
│  ## 🏛️ POSSIBLE LEGAL PROCEDURES                                        │
│  - File a civil suit for recovery of money                              │
│  - Approach the Rent Controller                                         │
│  ...                                                                    │
│                                                                         │
│  ## ⚠️ IMPORTANT DISCLAIMER                                             │
│  This analysis is for informational purposes only...                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Data Flow Pipeline

### 5.1 — Chat Analysis Flow (Primary Use Case)

```
 User types situation
         │
         ▼
 ┌─── FRONTEND ───┐
 │ chat/page.tsx   │
 │ handleSubmit()  │
 └───────┬─────────┘
         │  POST /api/v1/chat/  { message, session_id }
         ▼
 ┌─── API ROUTE ──────────┐
 │ routes/chat.py          │
 │                         │
 │ 1. Upsert ChatSession   │──── PostgreSQL (chat_sessions)
 │ 2. Save user message    │──── PostgreSQL (chat_messages)
 │ 3. Call RAG Pipeline    │
 └───────┬─────────────────┘
         │
         ▼
 ┌─── RAG PIPELINE ────────────────────────────────────────────┐
 │ rag_pipeline.py → analyze_situation()                        │
 │                                                              │
 │  ┌──────────────────────┐   ┌──────────────────────┐        │
 │  │  VECTOR SEARCH       │   │  KEYWORD SEARCH      │        │
 │  │  ChromaDB             │   │  PostgreSQL           │        │
 │  │                      │   │                      │        │
 │  │  Input: situation    │   │  Input: terms from   │        │
 │  │  Output: top N laws  │   │  situation split     │        │
 │  │  (cosine similarity) │   │  Output: matching    │        │
 │  │                      │   │  law_sections rows   │        │
 │  └──────────┬───────────┘   └──────────┬───────────┘        │
 │             │                          │                     │
 │             └──────────┬───────────────┘                     │
 │                        │                                     │
 │                        ▼                                     │
 │              ┌─────────────────┐                             │
 │              │  MERGE + DEDUP  │                             │
 │              │  Vector first,  │                             │
 │              │  then SQL       │                             │
 │              └────────┬────────┘                             │
 │                       │                                      │
 │                       ▼                                      │
 │              ┌─────────────────┐                             │
 │              │  FORMAT FOR LLM │                             │
 │              │  laws → text    │                             │
 │              └────────┬────────┘                             │
 │                       │                                      │
 └───────────────────────┼──────────────────────────────────────┘
                         │
                         ▼
 ┌─── IRAC ENGINE ────────────────────────────────┐
 │ reasoning.py → analyze()                        │
 │                                                  │
 │  System Prompt: IRAC rules + output format      │
 │  Human Prompt:  situation + formatted laws       │
 │                                                  │
 │        ┌──────────────────────┐                 │
 │        │  LLM API CALL        │                 │
 │        │  (OpenAI / Claude /  │                 │
 │        │   Ollama)            │                 │
 │        └──────────┬───────────┘                 │
 │                   │                              │
 │                   ▼                              │
 │        Markdown analysis (7 sections)           │
 └────────────────────┬────────────────────────────┘
                      │
                      ▼
 ┌─── API ROUTE ──────────┐
 │ routes/chat.py          │
 │                         │
 │ 4. Save AI response     │──── PostgreSQL (chat_messages)
 │ 5. Build ChatResponse   │
 └───────┬─────────────────┘
         │  JSON { session_id, analysis, relevant_sections[], timestamp }
         ▼
 ┌─── FRONTEND ───────────┐
 │ chat/page.tsx           │
 │                         │
 │ • Render markdown       │
 │ • Show section badges   │
 │ • Update chat history   │
 └─────────────────────────┘
```

### 5.2 — Law Search Flow

```
 User types keyword + selects category
         │
         ▼
 search/page.tsx → searchLaws(query, category)
         │  GET /api/v1/laws/search?q=theft&category=criminal&limit=20
         ▼
 routes/laws.py → search_laws()
         │
         ▼
 RAGPipeline.search_laws(query, category, limit)
         │
         ├── ChromaDB vector search (semantic)
         ├── PostgreSQL ILIKE keyword search
         └── Merge + deduplicate
         │
         ▼
 Return SearchResponse { query, results[], total }
         │
         ▼
 search/page.tsx → renders LawCard components (expandable)
```

### 5.3 — Section Explorer Flow

```
 Page loads
         │
         ▼
 explore/page.tsx → getActs()
         │  GET /api/v1/laws/acts
         ▼
 routes/laws.py → get_acts()
         │  SELECT DISTINCT act_name FROM law_sections
         ▼
 Sidebar shows act list
         │
 User clicks an act
         │
         ▼
 explore/page.tsx → getSectionsByAct(actName)
         │  GET /api/v1/laws/sections/{actName}
         ▼
 routes/laws.py → get_sections_by_act()
         │  SELECT * FROM law_sections WHERE act_name ILIKE '%..%' ORDER BY section_number
         ▼
 Right panel shows expandable section cards
```

---

## 6. Database Architecture

### 6.1 — PostgreSQL Schema (Entity-Relationship)

```
┌──────────────────────────────────┐
│         legal_categories         │
├──────────────────────────────────┤
│ id          SERIAL    PK         │
│ name        VARCHAR(200) UNIQUE  │
│ slug        VARCHAR(100) UNIQUE  │
│ description TEXT                  │
└──────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────┐
│                         law_sections                              │
├──────────────────────────────────────────────────────────────────┤
│ id                SERIAL       PK                                │
│ act_name          VARCHAR(500) NOT NULL          INDEX            │
│ section_number    VARCHAR(50)  NOT NULL                           │
│ title             VARCHAR(1000) NOT NULL                          │
│ description       TEXT         NOT NULL                           │
│ keywords          TEXT         NULLABLE  (comma-separated)        │
│ category          VARCHAR(100) NOT NULL          INDEX            │
│ punishment        TEXT         NULLABLE                           │
│ old_law_reference VARCHAR(500) NULLABLE  (e.g. "IPC Sec 302")    │
│ is_active         BOOLEAN      DEFAULT true                      │
│ created_at        TIMESTAMPTZ  DEFAULT now()                     │
│ updated_at        TIMESTAMPTZ  ON UPDATE now()                   │
├──────────────────────────────────────────────────────────────────┤
│ UNIQUE INDEX: idx_act_section (act_name, section_number)         │
└──────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────┐       ┌──────────────────────────────┐
│         chat_sessions            │       │        chat_messages          │
├──────────────────────────────────┤       ├──────────────────────────────┤
│ id         SERIAL    PK         │   1:N │ id          SERIAL    PK     │
│ session_id VARCHAR(100) UNIQUE  │◄──────│ session_id  INTEGER   FK     │
│ created_at TIMESTAMPTZ          │       │ role        VARCHAR(20)      │
└──────────────────────────────────┘       │ content     TEXT             │
                                           │ created_at  TIMESTAMPTZ     │
                                           └──────────────────────────────┘
```

### 6.2 — ChromaDB Vector Store

```
Collection: "indian_laws"
Distance metric: Cosine (HNSW index)
Storage: DuckDB + Parquet (persisted to disk)

Each document:
┌─────────────────────────────────────────────────────────────────────────┐
│ id:       "1"  (matches law_sections.id)                                │
│ document: "Bharatiya Nyaya Sanhita, 2023 — Section 100: Murder\n..."   │
│ metadata: {                                                             │
│   act_name: "Bharatiya Nyaya Sanhita, 2023",                           │
│   section_number: "100",                                                │
│   title: "Murder",                                                      │
│   category: "criminal",                                                 │
│   punishment: "Death or imprisonment for life...",                      │
│   old_law_reference: "Indian Penal Code, Section 302"                  │
│ }                                                                       │
│ embedding: [0.023, -0.114, 0.087, ...]  (auto-generated by ChromaDB)   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.3 — Why Two Databases?

| Concern | PostgreSQL | ChromaDB |
|---------|-----------|----------|
| **Query type** | Exact match, keyword ILIKE, structured queries | Semantic similarity ("situations like mine") |
| **Strength** | Precise section lookup, act browsing, category filtering | Understanding intent even with different vocabulary |
| **Example** | "Show me Section 100 of BNS" | "Someone killed my brother" → finds murder provisions |
| **Data model** | Relational rows with typed columns | Flat document + embedding vectors |
| **Persistence** | Full ACID transactions | File-based (DuckDB + Parquet) |

The RAG pipeline queries **both** and merges results — this ensures we never miss a relevant provision whether the user uses legal terminology or plain language.

---

## 7. API Contract

### Complete Endpoint Table

| Method | Path | Request Body | Response | Description |
|--------|------|-------------|----------|-------------|
| `GET` | `/` | — | `{ name, version, description, docs, health }` | System info |
| `GET` | `/api/v1/health` | — | `HealthResponse` | Database + vector store status |
| `POST` | `/api/v1/chat/` | `ChatRequest` | `ChatResponse` | Chat-based legal analysis |
| `POST` | `/api/v1/analyze/` | `AnalyzeRequest` | `LegalAnalysis` | Structured deep analysis |
| `GET` | `/api/v1/laws/search?q=&category=&limit=` | — | `SearchResponse` | Hybrid law search |
| `GET` | `/api/v1/laws/sections/{act_name}` | — | `LawSectionResponse[]` | Sections of an act |
| `GET` | `/api/v1/laws/categories` | — | `[{id, name, slug, description}]` | All categories |
| `GET` | `/api/v1/laws/acts` | — | `[{act_name}]` | All distinct acts |
| `GET` | `/api/v1/laws/{law_id}` | — | `LawSectionResponse` | Single section detail |

### Auto-Generated Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 8. AI Reasoning Engine Design

### IRAC Framework Implementation

```
                    ┌──────────────────────────────────────┐
                    │        IRAC SYSTEM PROMPT             │
                    │        (constants.py)                 │
                    │                                      │
                    │  CORE PRINCIPLES:                    │
                    │  • Never declare guilt/innocence     │
                    │  • Only present interpretations      │
                    │  • Not a lawyer, not a judge         │
                    │  • Always cite sections              │
                    │  • Multiple perspectives             │
                    │                                      │
                    │  OUTPUT FORMAT:                      │
                    │  7 mandatory sections                │
                    │  (Fact Summary → ... → Disclaimer)   │
                    │                                      │
                    │  GUIDELINES:                         │
                    │  • Simple language                   │
                    │  • Old + new law references          │
                    │  • Mention jurisdiction              │
                    │  • Multi-area separation             │
                    └────────────────┬─────────────────────┘
                                     │
                                     │  System message
                                     ▼
┌──────────────┐           ┌─────────────────────────┐           ┌───────────────┐
│              │  Human    │                         │  API call │               │
│  User's      │  message  │    LangChain            │──────────▶│  LLM          │
│  situation   │──────────▶│    ChatPromptTemplate   │           │  (GPT-4 /     │
│  +           │           │    prompt | llm         │◀──────────│   Claude /    │
│  Retrieved   │           │                         │  Response │   Mistral)    │
│  laws text   │           └─────────────────────────┘           │               │
│              │                                                  └───────────────┘
└──────────────┘

                                     │
                                     ▼
                    ┌──────────────────────────────────────┐
                    │  STRUCTURED MARKDOWN OUTPUT           │
                    │                                      │
                    │  ⚖️  FACT SUMMARY                     │
                    │  📋 LEGAL QUESTIONS                   │
                    │  📖 RELEVANT LAWS                     │
                    │  🔍 LEGAL INTERPRETATION              │
                    │  📎 EVIDENCE COMMONLY REQUIRED        │
                    │  🏛️  POSSIBLE LEGAL PROCEDURES        │
                    │  ⚠️  IMPORTANT DISCLAIMER             │
                    └──────────────────────────────────────┘
```

### Guardrail Implementation

The IRAC prompt enforces neutrality at three levels:

1. **System-level**: The prompt identity says "you are NOT a lawyer and NOT a judge"
2. **Output-level**: The mandatory disclaimer section is part of the format specification
3. **Application-level**: The `SAFETY_DISCLAIMER` constant is also injected programmatically in the `/analyze` endpoint response

---

## 9. RAG Retrieval Pipeline Design

```
         User: "My neighbor hit me during an argument"
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ▼                ▼                ▼
    ┌────────────┐   ┌────────────┐   ┌────────────┐
    │ "neighbor" │   │   "hit"    │   │ "argument" │     Term extraction
    │ "during"   │   │            │   │            │     (words > 2 chars)
    └────────────┘   └────────────┘   └────────────┘
           │                │                │
           │     PARALLEL SEARCH PATHS       │
           │                │                │
    ╔══════╧════════════════╧════════════════╧══════╗
    ║                                               ║
    ║   PATH A: VECTOR SEARCH (ChromaDB)            ║
    ║                                               ║
    ║   Full situation text → embedding →            ║
    ║   cosine similarity against all law            ║
    ║   document embeddings                         ║
    ║                                               ║
    ║   Returns: Top N semantically similar laws    ║
    ║   Example matches:                            ║
    ║   • BNS §115 "Voluntarily causing hurt"       ║
    ║   • BNS §351 "Criminal Intimidation"          ║
    ║   • BNS §101 "Culpable Homicide"             ║
    ║                                               ║
    ╠═══════════════════════════════════════════════╣
    ║                                               ║
    ║   PATH B: KEYWORD SEARCH (PostgreSQL)         ║
    ║                                               ║
    ║   WHERE keywords ILIKE '%hit%'                ║
    ║      OR title ILIKE '%hit%'                   ║
    ║      OR description ILIKE '%hit%'             ║
    ║      OR keywords ILIKE '%neighbor%'           ║
    ║      OR ...  (OR across all terms × 3 cols)   ║
    ║                                               ║
    ║   Returns: Matching law_sections rows         ║
    ║   Example matches:                            ║
    ║   • BNS §115 "Voluntarily causing hurt"       ║
    ║   • DV Act §3 "Domestic violence" (if family) ║
    ║                                               ║
    ╚═══════════════════╤═══════════════════════════╝
                        │
                        ▼
              ┌──────────────────┐
              │   MERGE + DEDUP  │
              │                  │
              │ 1. All vector    │
              │    results       │
              │ 2. SQL results   │
              │    not in set    │
              │ 3. Dedupe by ID  │
              │ 4. Cap at limit  │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  FORMAT FOR LLM  │
              │                  │
              │  Each law →      │
              │  numbered block: │
              │  • Act name      │
              │  • Section       │
              │  • Title         │
              │  • Full text     │
              │  • Punishment    │
              │  • Old law ref   │
              └────────┬─────────┘
                       │
                       ▼
              Passed to IRACReasoningEngine.analyze()
```

---

## 10. Security & Guardrails

### Legal Neutrality Enforcement

| Layer | Mechanism |
|-------|----------|
| **Prompt engineering** | IRAC_SYSTEM_PROMPT explicitly forbids declaring guilt/innocence |
| **Output format** | Mandatory 7-section structure forces balanced analysis |
| **Programmatic disclaimer** | `SAFETY_DISCLAIMER` constant appended in API response |
| **Frontend disclaimer** | Persistent disclaimer shown below chat input at all times |
| **Landing page** | Dedicated disclaimer section with ⚠️ icon |

### Input Validation

| Field | Constraint |
|-------|-----------|
| `ChatRequest.message` | 10–5,000 characters |
| `AnalyzeRequest.situation` | 20–10,000 characters |
| `LawSearchRequest.query` | 2–200 characters |
| `limit` parameter | 1–50 |

### CORS

Restricted to `http://localhost:3000` by default (configurable via `CORS_ORIGINS` in `.env`).

---

*End of Architecture Document*
