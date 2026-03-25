# VANI Copilot - AI Customer Support Copilot

An AI-powered customer support copilot for Vietnamese e-commerce stores. The system uses Retrieval-Augmented Generation (RAG) with fine-tuned models to suggest accurate, brand-consistent replies to customer queries.

## Problem Statement

Vietnamese e-commerce shops handle hundreds of repetitive customer messages daily (sizing, shipping, returns, promotions). Human agents spend 60-70% of their time on questions already answered in store policies. VANI Copilot acts as an AI assistant for human agents — retrieving relevant knowledge and generating suggested replies in the correct tone and style.

## Architecture

```
Customer Message → FastAPI Backend → Embedding Model → FAISS Retrieval
                                                           ↓
                                   ← Streaming Response ← LLM (Fine-tuned)
```

### Key Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend API | FastAPI + Python 3.11 | REST API with SSE streaming |
| Vector Store | FAISS | Fast similarity search over knowledge base |
| Embedding | multilingual-e5 (fine-tuned) | Encode queries and documents |
| LLM | Llama 3.1 8B QLoRA (via Ollama) | Generate customer support replies |
| Frontend | React 18 + Tailwind CSS 4 | Modern chat UI with dark mode |
| Database | SQLite (aiosqlite) | Conversation history and feedback |
| Containerization | Docker Compose | One-command deployment |

### Fine-tuning (3 Layers)

1. **Embedding Model** — Fine-tune `intfloat/multilingual-e5-base` with contrastive learning on Vietnamese CSKH queries
2. **LLM** — Fine-tune `Llama 3.1 8B Instruct` with QLoRA on Vietnamese customer support conversations
3. **Re-ranker** — Fine-tune `BAAI/bge-reranker-base` to improve retrieval precision

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── core/          # Config, security, middleware
│   │   ├── data/          # Knowledge base (policies, FAQ, products)
│   │   ├── models/        # Pydantic schemas, SQLAlchemy models
│   │   ├── prompts/       # LLM prompt templates
│   │   ├── routes/        # API endpoints (chat, conversations, admin)
│   │   └── services/      # Business logic (RAG, LLM, retriever, embedding)
│   ├── scripts/           # build_index.py, download_data.py
│   ├── vectorstore/       # FAISS index files
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/    # Chat UI, Layout, Sidebar
│       ├── hooks/         # useChat custom hook
│       ├── services/      # API client
│       ├── store/         # Zustand state management
│       └── types/         # TypeScript interfaces
├── notebooks/
│   ├── 01_data_preparation.ipynb
│   ├── 02_finetune_llm_qlora.ipynb
│   ├── 03_finetune_embedding.ipynb
│   ├── 04_finetune_reranker.ipynb
│   └── 05_evaluation.ipynb
└── docker-compose.yml
```

## Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.ai/) (for local LLM inference)

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

# Build FAISS index from knowledge base
python scripts/build_index.py

# Create .env from template
cp .env.example .env
# Edit .env with your settings (LLM provider, API keys, etc.)

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173, proxies `/api` to backend.

### 3. LLM Setup

**Option A: Ollama (recommended for fine-tuned model)**
```bash
ollama serve
ollama pull llama3.1:8b
# Or use the fine-tuned GGUF model:
# ollama create vani-copilot -f Modelfile
```

**Option B: OpenAI API**
Set in `.env`:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 4. Docker (Full Stack)

```bash
docker compose up --build
```
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Ollama: http://localhost:11434

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/chat` | Send message, get reply |
| POST | `/api/chat/stream` | Send message, stream reply (SSE) |
| GET | `/api/conversations` | List all conversations |
| GET | `/api/conversations/{id}` | Get conversation detail |
| POST | `/api/feedback` | Submit feedback on a reply |
| POST | `/api/admin/upload` | Upload knowledge document |
| POST | `/api/admin/rebuild-index` | Rebuild FAISS index |
| GET | `/api/admin/chunks` | View indexed chunks |

All API endpoints (except `/health`) require `X-API-Key` header.

## Fine-tuning Pipeline

The notebooks in `notebooks/` provide a complete fine-tuning pipeline for Google Colab Pro:

1. **01_data_preparation.ipynb** — Download, clean, merge 3 Vietnamese datasets into ChatML format
2. **02_finetune_llm_qlora.ipynb** — Fine-tune Llama 3.1 8B with QLoRA, export to GGUF
3. **03_finetune_embedding.ipynb** — Fine-tune multilingual-e5 with contrastive learning
4. **04_finetune_reranker.ipynb** — Fine-tune BGE re-ranker for improved retrieval
5. **05_evaluation.ipynb** — Evaluate retrieval (Recall@k) and generation (BLEU, ROUGE-L, BERTScore)

### Datasets Used

| Dataset | Source | Size | Type |
|---------|--------|------|------|
| CSConDa | ura-hcmut/Vietnamese-Customer-Support-QA | 9,849 | Real Vietnamese CSKH QA |
| Ecommerce Chat | 5CD-AI/Vietnamese-Ecommerce-Multi-turn-Chat | 1,482 | E-commerce multi-turn |
| Alpaca Chat | 5CD-AI/Vietnamese-Multi-turn-Chat-Alpaca | 12,697 | General Vietnamese (filtered) |

## Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy, FAISS, Sentence-Transformers
- **Frontend:** React 18, Tailwind CSS 4, Zustand, Framer Motion, Lucide Icons
- **ML/AI:** Llama 3.1 8B (QLoRA), multilingual-e5 (contrastive), BGE re-ranker
- **Infra:** Docker Compose, Ollama, Nginx, SQLite
