# YAMA AI — Indian Justice Analysis System

A neutral legal analysis platform powered by AI that helps Indian citizens understand legal implications of real-life situations using the IRAC (Issue, Rule, Application, Conclusion) framework.

> **Disclaimer**: YAMA AI provides legal information and analysis only. It does NOT provide legal advice, does NOT declare guilt or innocence, and does NOT replace consultation with a qualified legal professional.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   Next.js        │────▶│   FastAPI         │────▶│   AI Reasoning      │
│   Frontend       │◀────│   Backend         │◀────│   Engine (IRAC)     │
│   (TailwindCSS)  │     │                  │     │   (LangChain)       │
└─────────────────┘     └──────┬───────────┘     └──────────┬──────────┘
                               │                            │
                    ┌──────────┴──────────┐      ┌──────────┴──────────┐
                    │   PostgreSQL        │      │   ChromaDB          │
                    │   (Structured Laws) │      │   (Vector Search)   │
                    └─────────────────────┘      └─────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 + TailwindCSS |
| Backend | Python FastAPI |
| AI Engine | LangChain + LLM (Claude/OpenAI/Ollama) |
| Vector DB | ChromaDB |
| Relational DB | PostgreSQL |
| Embeddings | sentence-transformers |

## Project Structure

```
yama-ai/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # API endpoint handlers
│   │   ├── core/                # Config, security, constants
│   │   ├── models/              # Pydantic models & DB schemas
│   │   ├── services/
│   │   │   ├── ai_engine/       # IRAC reasoning engine
│   │   │   └── retrieval_engine/# RAG pipeline
│   │   └── db/                  # Database connections
│   ├── legal_database/seeds/    # Seed data for laws
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js pages
│   │   ├── components/          # React components
│   │   ├── lib/                 # Utilities
│   │   └── types/               # TypeScript types
│   └── package.json
├── docs/
│   ├── ARCHITECTURE.md          # System architecture details
│   ├── INGESTION.md             # Ingestion pipeline guide
│   └── project-notes/           # Setup, status, and progress notes
├── docker-compose.yml
└── README.md
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Ingestion Guide](docs/INGESTION.md)
- [Backend Manual Guide](docs/project-notes/BACKEND_MANUAL_GUIDE.md)
- [Backend Setup Guide](docs/project-notes/BACKEND_SETUP_GUIDE.md)
- [Features Added](docs/project-notes/FEATURES_ADDED.md)
- [Features Guide](docs/project-notes/FEATURES_GUIDE.md)
- [Final Status](docs/project-notes/FINAL_STATUS.md)
- [Fix Chat Error](docs/project-notes/FIX_CHAT_ERROR.md)
- [Next Steps](docs/project-notes/NEXT_STEPS.md)
- [System Summary](docs/project-notes/SYSTEM_SUMMARY.md)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Git

### 1. Clone & Setup Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

### 3. Setup Database

```bash
# Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE yama_ai;"

# Run migrations and seed data
python -m app.db.init_db
```

### 4. Start Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 5. Setup & Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### 6. Open Application

Navigate to `http://localhost:3000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat` | Submit a situation for legal analysis |
| GET | `/api/v1/laws/search` | Search laws by keyword |
| GET | `/api/v1/laws/sections/{act}` | Browse sections of a specific act |
| GET | `/api/v1/laws/{id}` | Get details of a specific law section |
| POST | `/api/v1/analyze` | Deep analysis of a legal situation |
| GET | `/api/v1/health` | Health check |

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `LLM_PROVIDER` | `openai`, `anthropic`, or `ollama` | Yes |
| `OPENAI_API_KEY` | OpenAI API key (if using OpenAI) | Conditional |
| `ANTHROPIC_API_KEY` | Anthropic API key (if using Claude) | Conditional |
| `OLLAMA_BASE_URL` | Ollama server URL (if using local models) | Conditional |
| `CHROMA_PERSIST_DIR` | ChromaDB persistence directory | No |

## Legal Disclaimer

YAMA AI is an educational and informational tool. It:
- Does **NOT** provide legal advice
- Does **NOT** declare guilt or innocence
- Does **NOT** replace qualified legal professionals
- Presents **possible legal interpretations** supported by Indian law
- Should be used for **informational purposes only**

Always consult a qualified advocate for legal matters.

## License

MIT License — See LICENSE for details.
