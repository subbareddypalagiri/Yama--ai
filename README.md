# YAMA AI — Indian Justice Analysis System

<div align="center">

![YAMA AI Badge](https://img.shields.io/badge/YAMA%20AI-v1.0.0-purple?style=flat-square&logo=scale)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)
![Node.js](https://img.shields.io/badge/Node.js-18%2B-green?style=flat-square&logo=node.js)
![Status](https://img.shields.io/badge/status-Active-brightgreen?style=flat-square)

**Democratizing Legal Intelligence in India**

Transform complex Indian legal documents into clear, actionable guidance using AI-powered IRAC analysis.

[Features](#-key-features) • [Quick Start](#-quick-start) • [API Routes](#-api-endpoints) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🎯 The Problem We Solve

Millions of Indian citizens face legal challenges every year—from property disputes to criminal accusations—yet **80% lack access to affordable legal counsel**. Meanwhile, legal research remains time-consuming, complex, and often inaccessible due to:

- **Information Asymmetry**: Laws are scattered across 100+ acts, rules, and notifications
- **Language Barriers**: Most resources are in English; citizens may understand Telugu, Hindi, or regional languages better
- **Analysis Paralysis**: Even when citizens find relevant laws, understanding application to their situation is daunting
- **Cost**: Professional legal consultation averages ₹5,000–₹50,000 per hour

**YAMA AI bridges this gap** by using advanced AI and Retrieval-Augmented Generation (RAG) to:
- ✅ Search Indian laws intelligently across 50+ acts and 10,000+ sections
- ✅ Analyze situations using IRAC framework (Issue → Rule → Application → Conclusion)
- ✅ Provide context-aware guidance in multiple languages
- ✅ Offer personal lawyer-mode for tailored legal advice
- ✅ Track cases and generate legal documents automatically

---

## ✨ Key Features

### 🤖 AI-Powered Legal Analysis
- **IRAC Framework**: Structured legal reasoning (Issue, Rule, Application, Conclusion)
- **Multi-Mode Analysis**: Quick answers, deep analysis, rights education, document drafting
- **Contextual Understanding**: Client profiles capture state jurisdiction and legal concerns
- **Fallback Intelligence**: Seamless LLM provider switching (Claude → OpenAI → Ollama)

### ⚖️ Your Personal Lawyer
- **Four Analysis Modes**:
  - 🏃 **Quick Advice**: 3-5 sentence direct answers
  - 📚 **Deep Analysis**: Full IRAC with case law precedents
  - 🛡️ **Know Your Rights**: Fundamental rights and available remedies
  - 📄 **Document Drafting**: Legal notices, FIRs, complaint templates
- **Client Profile Tracking**: Remembers name, state, and legal concern across sessions
- **Session History**: Maintains conversation context for continuity

### 📚 A-to-Z Legal Data
- **50+ Indian Acts**: BNS, BNSS, IPC, CrPC, Constitution, IT Act, Consumer Protection Act, etc.
- **Supreme & High Court Judgments**: 50+ lakh case precedents from Indian Kanoon
- **State-Specific Laws**: Tailored guidance for all 28 Indian states + UTs
- **Real-Time Updates**: Automated crawler keeps legal database fresh
- **Deduplication**: SHA-256 hashing ensures zero duplicate records

### 🔍 Intelligent Retrieval
- **Vector Search**: Semantic similarity matching using sentence-transformers
- **RAG Pipeline**: Combines retrieval + generation for accuracy
- **Category Intelligence**: Auto-classifies laws (criminal, civil, family, labor, etc.)
- **Keyword Extraction**: Surfaces relevant law sections in seconds

### 📋 Case & Document Management
- **Case Tracking**: Create, update, and monitor cases with AI-generated summaries
- **Document Upload & Analysis**: OCR + entity extraction + legal relevance scoring
- **Report Generation**: Automated case reports with timeline and analysis
- **Evidence Preservation**: Timestamp and categorize legal documents

### 🌍 Multi-Language Support
- English, Telugu, Hindi, and more
- Live translation via Google Cloud Translate
- Transliteration for regional script support
- Language detection auto-activates right interface

### 🎨 Premium User Experience
- **Dark Mode with VenusHawk-style UI**: Glowing cards, neural backgrounds, smooth animations
- **Responsive Design**: Works seamlessly on desktop, tablet, mobile
- **Accessibility First**: WCAG 2.1 compliant with keyboard navigation
- **Real-Time Feedback**: Live-updating chat, progress indicators, error handling

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (3001)                         │
│         Next.js 14 + TailwindCSS + React 19                     │
│    ┌────────────┬───────────┬──────────┬──────────┐             │
│    │    Chat    │   Laws    │  Cases   │  Lawyer  │             │
│    │            │  Search   │ Tracking │  (NEW)   │             │
│    └─────┬──────┴────┬──────┴────┬─────┴────┬─────┘             │
└─────────┼───────────┼───────────┼──────────┼───────────────────┘
          │           │           │          │
          └───────────┼───────────┴──────────┘
                      │
          ┌───────────▼──────────────┐
          │  Next.js Rewrite Proxy   │
          │  /api/* → http://8000    │
          └───────────┬──────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────────┐
│                      Backend (8000)                            │
│              FastAPI + Python + SQLAlchemy                     │
│   ┌──────────────────────────────────────────────────────┐    │
│   │            API Routes (@/api/v1)                    │    │
│   │  ┌─────────┬─────────┬─────────┬────────────────┐   │    │
│   │  │  Chat   │  Laws   │  Cases  │  Lawyer(NEW)   │   │    │
│   │  ├─────────┼─────────┼─────────┼────────────────┤   │    │
│   │  │Analyze  │Documents│ Reports │ Ingestion      │   │    │
│   │  └─────────┴─────────┴─────────┴────────────────┘   │    │
│   └──────────────┬─────────────────────────────────────┘    │
│   ┌─────────────┴─────────────────┬──────────────────┐      │
│   │                               │                  │      │
│   ▼                               ▼                  ▼      │
│  AI Engine                   RAG Pipeline      Data Pipeline │
│  ┌──────────────┐          ┌──────────────┐  ┌────────────┐ │
│  │ LangChain    │          │ Embeddings   │  │ Crawler v2 │ │
│  │ LLM Router   │          │ + ChromaDB   │  │ (A-to-Z)   │ │
│  │ (Claude/GPT) │          │ + Retrieval  │  │ (Active)   │ │
│  └──────────────┘          └──────────────┘  └────────────┘ │
└─────────────────────────────┬─────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
        SQLite            ChromaDB         Chroma Index
        (Law DB)          (Vectors)        (187 docs)
```

---

## 🚀 Quick Start

### Prerequisites
- **Python** 3.11+
- **Node.js** 18+
- **npm** or **yarn**

### 1️⃣ Clone Repository
```bash
git clone https://github.com/subbareddypalagiri/Yama--ai.git
cd Yama--ai
```

### 2️⃣ Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations & seed database
python -c "from app.db.init_db import seed_laws; seed_laws()"

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

**Backend runs on**: `http://localhost:8000`

### 3️⃣ Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Next.js dev server
npm run dev
```

**Frontend runs on**: `http://localhost:3001`

### ✅ Verify Installation
- Frontend: Open `http://localhost:3001` in your browser
- Backend: Check health endpoint `http://localhost:8000/api/v1/health`
- Try the chat or lawyer features

---

## 📡 API Endpoints

All endpoints are prefixed with `/api/v1`

### 🤖 Chat & Analysis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat/` | POST | Send legal question and get IRAC analysis |
| `/analyze-situation` | POST | Analyze a legal situation |
| `/health` | GET | System health check |

### ⚖️ Your Lawyer (NEW)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/lawyer/` | POST | **Personal lawyer with multi-mode analysis** |

**Lawyer Modes**:
- `quick` - Fast 3-5 sentence answers
- `deep` - Full IRAC analysis with case law
- `rights` - Constitutional & legal rights guidance
- `document` - Draft legal documents

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/lawyer/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can my landlord evict me without 2 months notice?",
    "mode": "rights",
    "client_profile": {
      "name": "Arjun",
      "state": "Karnataka",
      "concern": "Property / Tenancy"
    }
  }'
```

### 📚 Laws & Search
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/laws/search` | GET | Search laws by keyword/category |
| `/laws/sections/{act_name}` | GET | Get all sections of an act |
| `/laws/{id}` | GET | Get specific law section |
| `/laws/acts` | GET | List all acts |
| `/laws/categories` | GET | Get all categories |

### 📋 Cases
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cases` | GET | List all cases |
| `/cases` | POST | Create new case |
| `/cases/{case_uid}` | GET | Get case details |
| `/cases/{case_uid}` | PATCH | Update case |
| `/cases/{case_uid}` | DELETE | Delete case |
| `/cases/{case_uid}/events` | GET | Get case timeline |
| `/cases/{case_uid}/events` | POST | Add case event |

### 📄 Documents
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/documents` | POST | Upload document |
| `/documents` | GET | List documents |
| `/documents/{doc_uid}/analyze` | POST | Analyze document with AI |
| `/documents/{doc_uid}` | DELETE | Delete document |

### 📊 Reports
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reports` | POST | Generate case report |
| `/reports` | GET | List reports |
| `/reports/{report_uid}/download` | GET | Download report |

---

## 🔧 Features Deep Dive

### Personal Lawyer Mode (`/lawyer`)
The **Your Lawyer** feature is a context-aware legal advisor that remembers your state, concern area, and preferred analysis depth.

#### Multi-Mode Analysis
```typescript
// Quick Mode: Direct, concise advice
"Can I refuse a breath test at a traffic stop?"
→ "Under IPC Section 185, refusing breath test can lead to 6-month jail..."

// Deep Mode: IRAC with case law
→ Issue: Right to refuse breath test?
   Rule: IPC §185, Bharti v. State (SC 2015)...
   Application: In your case...
   Conclusion: You have limited rights...

// Rights Mode: Fundamental protections
→ Constitutional Right: Article 20(3) protects self-incrimination...
   Remedies: File bail petition, habeas corpus...

// Document Mode: Templates & drafts
→ Here's a drunk driving charge bail petition template...
```

#### Session Persistence
- Chat history stored per session
- Client profile remembered across interactions
- Relevant laws auto-surfaced based on concern area

### A-to-Z Legal Data Crawler v2

**Run the crawler**:
```bash
# Option 1: All sources (comprehensive)
python -m data_pipeline.crawler_v2 --source all

# Option 2: Only Indian Kanoon (50+ lakh judgments)
python -m data_pipeline.crawler_v2 --source indian_kanoon --pages 200

# Option 3: Only India Code (central acts)
python -m data_pipeline.crawler_v2 --source india_code

# Windows users: Use the helper script
.\backend\data_pipeline\run_crawler.sh  # or run_crawler.bat (NEW)
```

**Sources Covered**:
- ✅ India Code (indiacode.nic.in) — All central acts
- ✅ Indian Kanoon (indiankanoon.org) — Supreme Court + HC + Tribunals
- ✅ Constitution — Articles, Schedules, Amendments
- ✅ eGazette — Notifications, Rules
- ✅ State Laws — 28 states
- ✅ NALSA — Legal Aid, Lok Adalat
- ✅ eCourts — District Court data

### RAG Pipeline
1. **Retrieval**: Vector search finds relevant laws based on semantic similarity
2. **Augmentation**: Retrieved laws + user query fed to LLM
3. **Generation**: LLM generates IRAC-structured response

---

## 🛠️ Development

### Adding a New API Route
```python
# backend/app/api/routes/my_feature.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/my-feature", tags=["My Feature"])

class MyRequest(BaseModel):
    query: str

@router.post("/analyze")
async def analyze(req: MyRequest):
    return {"result": "Analysis here"}
```

Then register in `main.py`:
```python
from app.api.routes.my_feature import router as my_router
app.include_router(my_router, prefix="/api/v1")
```

### Adding a Frontend Page
```bash
# Create new page directory
mkdir frontend/src/app/my-feature

# Add page.tsx
touch frontend/src/app/my-feature/page.tsx
```

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Detailed system design |
| [INGESTION.md](docs/INGESTION.md) | Data pipeline & crawling |
| [BACKEND_SETUP_GUIDE.md](docs/project-notes/BACKEND_SETUP_GUIDE.md) | Backend configuration |
| [FEATURES_GUIDE.md](docs/project-notes/FEATURES_GUIDE.md) | Using each feature |
| [FINAL_STATUS.md](docs/project-notes/FINAL_STATUS.md) | Implementation status |

---

## 🤝 Contributing

We ❤️ contributions! Here's how to help:

### Report Issues
1. Check [existing issues](https://github.com/subbareddypalagiri/Yama--ai/issues)
2. Create a new issue with:
   - Clear title & description
   - Steps to reproduce
   - Expected vs. actual behavior

### Submit Code
1. Fork the repo
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Code Standards
- Backend: PEP 8 + type hints
- Frontend: ESLint + Prettier
- Commit messages: Conventional Commits
- Tests: Pytest (backend), Vitest (frontend)

---

## ⚠️ Important Disclaimer

**YAMA AI provides legal *information*, not legal *advice*.**

- ❌ YAMA AI cannot replace a qualified lawyer
- ❌ YAMA AI does not declare guilt or innocence
- ❌ Use YAMA AI analysis only as reference material
- ✅ Always consult with a licensed advocate for legal matters
- ✅ YAMA AI helps understand laws and identify issues

**For immediate legal help**, contact:
- **National Law Commission**: nalsa.gov.in
- **Bar Council of India**: bcci.in
- **Legal Aid Services**: Your state's high court

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Acts Covered** | 50+ |
| **Sections Indexed** | 10,000+ |
| **Judgments Available** | 50+ lakh |
| **States Supported** | 28 + UTs |
| **Languages** | 5+ |
| **API Routes** | 25+ |
| **Vector Index Size** | 187+ docs |

---

## 🎯 Roadmap

### v1.1 (June 2026)
- [ ] Mobile app (React Native)
- [ ] Video legal tutorials
- [ ] Community Q&A forum

### v1.2 (July 2026)
- [ ] Lawyer directory integration
- [ ] Automated legal notice generation
- [ ] Court filing assistance

### v2.0 (Q3 2026)
- [ ] Multi-jurisdiction support (US, UK, Singapore)
- [ ] Blockchain-based document notarization
- [ ] Real-time court hearing updates

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) file for details.

---

## 👥 Team

- **Created by**: Subba Reddy Palagiri
- **Special Thanks**: To all legal experts and open-source contributors

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/subbareddypalagiri/Yama--ai/issues)
- **Email**: subbareddy123sub@gmail.com
- phone no =9493811060

---

<div align="center">

**Made with ❤️ for Indian Justice System**

⭐ If you find YAMA AI helpful, please give it a star!

</div>
