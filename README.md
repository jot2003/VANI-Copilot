# VANI Copilot — AI Customer Support Copilot

An AI-powered customer support copilot for Vietnamese e-commerce (fashion). The system uses **Retrieval-Augmented Generation (RAG)** with **3-layer fine-tuned models** and a **LangChain Agent** to suggest accurate, brand-consistent replies to customer queries.

## Problem Statement

Vietnamese e-commerce shops handle hundreds of repetitive customer messages daily (sizing, shipping, returns, promotions). Human agents spend 60-70% of their time on questions already answered in store policies. **VANI Copilot** acts as an AI assistant for human agents — retrieving relevant knowledge and generating suggested replies in the correct tone and style.

## Architecture

```
Customer Message
    ↓
FastAPI Backend (API Key Auth + Rate Limiting + Request Tracing)
    ↓
┌─── Agent Router (LangChain) ───────────────────────────────┐
│  Intent Classification → Tool Selection                     │
│                                                             │
│  Tools:                                                     │
│  ├── search_knowledge_base  → RAG Pipeline                  │
│  ├── track_order            → Order Status API              │
│  ├── search_products        → Product Catalog               │
│  └── request_human_handoff  → Escalation                    │
└─────────────────────────────────────────────────────────────┘
    ↓
RAG Pipeline: Embedding → FAISS Retrieval → Re-ranking → LLM
    ↓
Streaming Response (SSE) → React Frontend
```

### Key Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend API | FastAPI + Python 3.11 | REST API with SSE streaming, rate limiting, request tracing |
| Agent | LangChain + Azure OpenAI | Intent classification, tool orchestration, confidence scoring |
| Vector Store | FAISS | Fast similarity search over knowledge base |
| Embedding | `multilingual-e5-base` (fine-tuned) | Encode queries and documents (768-dim) |
| Re-ranker | `CrossEncoder` (fine-tuned) | Re-score candidates for higher retrieval precision |
| LLM | Llama 3.1 8B QLoRA (Ollama) / Azure OpenAI | Generate customer support replies |
| Frontend | React 18 + Tailwind CSS 4 + Framer Motion | Premium dark-mode chat UI with markdown rendering |
| Database | SQLite (aiosqlite) | Conversations, messages, feedback, analytics events |
| Deployment | Docker Compose + Nginx | Production-ready containerized deployment |

### Fine-tuning (3 Layers)

1. **Embedding Model** — Fine-tune `intfloat/multilingual-e5-base` with contrastive learning on Vietnamese CSKH queries
2. **LLM** — Fine-tune `Llama 3.1 8B Instruct` with QLoRA on Vietnamese customer support conversations
3. **Re-ranker** — Fine-tune `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` to improve retrieval precision

## Features

### Core
- **Agent-based routing** — LangChain agent classifies intent and selects appropriate tools
- **RAG with re-ranking** — FAISS retrieval → CrossEncoder re-ranking → context-aware LLM generation
- **Multi-provider LLM** — Ollama (local fine-tuned), Azure OpenAI, OpenAI API
- **SSE streaming** — Real-time token-by-token response streaming
- **Conversation history** — Persistent SQLite storage with multi-turn context

### Production Robustness
- **API key authentication** — `X-API-Key` header on all protected endpoints
- **Rate limiting** — Configurable per-minute limits (SlowAPI)
- **Request tracing** — Auto-generated `X-Request-ID` on every request
- **LLM retry** — Exponential backoff with tenacity (3 attempts)
- **Agent timeout** — `asyncio.wait_for` with configurable timeout, fallback to direct RAG
- **Structured errors** — JSON error responses with request_id for debugging
- **Graceful shutdown** — Resource cleanup on application exit

### Frontend
- **Premium dark-mode UI** — Glassmorphism design, gradient accents, smooth animations
- **Markdown rendering** — AI responses rendered with full markdown support
- **Stop generation** — Cancel streaming mid-response with AbortController
- **Confidence meter** — Visual indicator of AI confidence per response
- **Toast notifications** — Copy, feedback, error notifications (Sonner)
- **Intent badges** — Visual classification of detected intent per response
- **Admin dashboard** — Knowledge base CRUD, analytics, intent distribution charts

### Admin & Analytics
- **Document CRUD** — Upload, create, update, delete knowledge base documents
- **Auto re-indexing** — FAISS index automatically rebuilt on document changes
- **Analytics dashboard** — Conversation counts, satisfaction rates, intent distribution
- **Feedback collection** — Thumbs up/down wired to backend for quality tracking

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── core/          # Config, security, middleware (rate limit, CORS, request ID)
│   │   ├── data/          # Knowledge base (policies, FAQ, products)
│   │   ├── models/        # Pydantic schemas, SQLAlchemy models
│   │   ├── prompts/       # LLM prompt templates
│   │   ├── routes/        # API endpoints (chat, conversations, admin, analytics, health)
│   │   └── services/      # Business logic (RAG, LLM, agent, retriever, reranker, embedding)
│   ├── tests/             # pytest test suite (35 tests)
│   ├── scripts/           # build_index.py, download_data.py
│   ├── vectorstore/       # FAISS index files
│   └── requirements.txt   # Pinned dependency versions
├── frontend/
│   └── src/
│       ├── components/    # Chat UI (markdown, confidence), Layout, Sidebar, Admin Dashboard
│       ├── hooks/         # useChat (streaming, stop generation)
│       ├── services/      # API client (SSE, AbortController)
│       ├── store/         # Zustand state management
│       └── types/         # TypeScript interfaces
├── models/                # Fine-tuned model weights (not in git)
│   ├── embedding-finetuned/
│   ├── reranker-finetuned/
│   └── vani-copilot-q3_k_m.gguf
├── notebooks/
│   ├── 01_data_preparation.ipynb
│   ├── 02_finetune_llm_qlora.ipynb
│   ├── 03_finetune_embedding.ipynb
│   ├── 04_finetune_reranker.ipynb
│   └── 05_evaluation.ipynb
└── docker-compose.yml
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Fine-tuned models in `models/` directory (see Fine-tuning Pipeline below)

### 1. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate  # or .\venv\Scripts\activate on Windows

pip install -r requirements.txt

# Build FAISS index from knowledge base
python scripts/build_index.py

# Create .env from template
cp .env.example .env
# Edit .env with your API keys and model paths

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173, proxies `/api` to backend.

### 3. LLM Provider

**Option A: Azure OpenAI (recommended)**
```env
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

**Option B: Ollama (local fine-tuned)**
```bash
ollama serve
ollama create vani-copilot -f Modelfile
```

**Option C: OpenAI API**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
```

### 4. Docker (Full Stack)

```bash
docker compose up --build
```
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Ollama: http://localhost:11434

### 5. Run Tests

```bash
cd backend
python -m pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check (no auth) |
| POST | `/api/chat` | Send message, get reply (agent or RAG) |
| POST | `/api/chat/stream` | Send message, stream reply (SSE) |
| GET | `/api/conversations` | List all conversations |
| GET | `/api/conversations/{id}` | Get conversation with messages |
| POST | `/api/feedback` | Submit thumbs up/down feedback |
| GET | `/api/analytics/overview` | Dashboard stats |
| GET | `/api/analytics/intents` | Intent distribution |
| GET | `/api/analytics/feedback` | Feedback list |
| GET | `/api/admin/documents` | List knowledge base documents |
| POST | `/api/admin/documents` | Create document + rebuild index |
| POST | `/api/admin/documents/upload` | Upload file + rebuild index |
| PUT | `/api/admin/documents/{id}` | Update document |
| DELETE | `/api/admin/documents/{id}` | Delete document + rebuild index |
| POST | `/api/admin/rebuild-index` | Manually rebuild FAISS index |
| GET | `/api/admin/chunks` | View all indexed chunks |

All API endpoints (except `/health`) require `X-API-Key` header.

## Fine-tuning Pipeline

The notebooks in `notebooks/` provide a complete fine-tuning pipeline for Google Colab Pro:

| Notebook | Model | Method | Output |
|----------|-------|--------|--------|
| 01 Data Preparation | — | Download, clean, merge 3 Vietnamese datasets | ChatML JSONL |
| 02 LLM Fine-tuning | Llama 3.1 8B | QLoRA (4-bit, r=64) | GGUF Q3_K_M |
| 03 Embedding | multilingual-e5-base | Contrastive learning | model.safetensors |
| 04 Re-ranker | mmarco-mMiniLMv2 | Cross-encoder training | model.safetensors |
| 05 Evaluation | All | Recall@k, BLEU, ROUGE-L, BERTScore | Metrics report |

### Datasets

| Dataset | Source | Size | Type |
|---------|--------|------|------|
| CSConDa | ura-hcmut/Vietnamese-Customer-Support-QA | 9,849 | Real Vietnamese CSKH QA |
| Ecommerce Chat | 5CD-AI/Vietnamese-Ecommerce-Multi-turn-Chat | 1,482 | E-commerce multi-turn |
| Alpaca Chat | 5CD-AI/Vietnamese-Multi-turn-Chat-Alpaca | 12,697 | General Vietnamese (filtered) |

## Configuration

All settings configurable via `.env`:

| Setting | Default | Description |
|---------|---------|-------------|
| `LLM_PROVIDER` | `azure` | LLM backend: `azure`, `ollama`, `openai` |
| `AGENT_ENABLED` | `true` | Enable LangChain agent routing |
| `RERANKER_ENABLED` | `true` | Enable CrossEncoder re-ranking |
| `LLM_TIMEOUT` | `120` | LLM request timeout (seconds) |
| `AGENT_TIMEOUT` | `60` | Agent execution timeout (seconds) |
| `RATE_LIMIT` | `30/minute` | API rate limit |
| `CORS_ORIGINS` | `localhost:5173,...` | Allowed CORS origins |
| `TOP_K_RETRIEVAL` | `20` | FAISS retrieval candidates |
| `TOP_K_RERANK` | `5` | Final re-ranked results |

See `.env.example` for the full list.

## Tech Stack

- **Backend:** Python 3.11, FastAPI, LangChain, SQLAlchemy, FAISS, Sentence-Transformers, tenacity, structlog
- **Frontend:** React 18, TypeScript, Tailwind CSS 4, Zustand, Framer Motion, react-markdown, Sonner, Lucide Icons
- **ML/AI:** Llama 3.1 8B (QLoRA), multilingual-e5-base (contrastive), CrossEncoder re-ranker
- **Infra:** Docker Compose, Nginx (gzip, security headers, SSE proxy), SQLite, Ollama
