# Wcore X - AI Chatbot Architecture

## Tổng quan Kiến trúc 4 Tầng

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   [ Người Dùng ] ──(1. Input)──► [ API & Guardrails ]                      │
│        ▲                                    │                               │
│        │                                    ▼                               │
│   [ Phản Hồi ] ◄──(4. Streaming)── [ LLM Core Engine ]                     │
│        │                                    ▲                               │
│        │                                    │                               │
│        └──────(2. Context)──────► [ RAG & Memory ]                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tầng 1: Tiếp Nhận & Lọc An Toàn (Input Layer)

### Mục tiêu
- Nhận input từ người dùng
- Tokenization (mã hóa văn bản)
- Guardrails (lọc an toàn)

### Code Implementation

```
src/ke/api/
├── server.py              # FastAPI server
├── routers/
│   ├── auth.py            # Xác thực người dùng
│   ├── api_keys.py        # Quản lý API Key
│   ├── chat.py            # Nhận message từ client
│   └── knowledge.py       # Tra cứu tri thức
└── middleware/
    ├── auth.py            # JWT Authentication
    └── rate_limiter.py    # Rate Limiting (60 req/min)
```

### Flow

```
Client (iOS/Web)
    │
    │ POST /api/chat/stream
    │ Headers: X-API-Key, Authorization
    │ Body: {"message": "...", "history": [...]}
    │
    ▼
┌─────────────────────────────────────┐
│  1. Rate Limiting (Redis)           │ ← 60 requests/minute
│  2. API Key Verification (SHA-256)  │ ← Xác thực client
│  3. Input Validation                │ ← Kiểm tra đầu vào
│  4. Prompt Injection Detection      │ ← Lọc tấn công
└─────────────────────────────────────┘
    │
    ▼
    Chuyển sang Tầng 2
```

### Key Components

| Component | File | Chức năng |
|-----------|------|-----------|
| Rate Limiter | `auth/rate_limiter.py` | Redis Sliding Window (60 req/min) |
| API Key Store | `auth/store.py` | SQLite lưu API keys (SHA-256 hash) |
| Auth Middleware | `auth/middleware.py` | Xác thực + Rate Limit |

---

## Tầng 2: Quản Lý Ngữ Cảnh & Tri Thức (Memory & RAG)

### Mục tiêu
- Nhớ ngữ cảnh hội thoại (Short-term memory)
- Lưu tri thức lâu dài (Long-term memory)
- Tìm kiếm tài liệu liên quan (RAG)

### Code Implementation

```
src/ke/cognitive/
├── engine.py              # Cognitive Engine (điều phối)
├── memory_integration.py  # Quản lý memory
├── rag_pipeline.py        # RAG retrieval
└── intent_detector.py     # Phát hiện ý định

src/ke/memory/
├── memory_manager.py      # Memory Manager
├── short_memory.py        # Bộ nhớ ngắn hạn
├── long_memory.py         # Bộ nhớ dài hạn
├── conversation_memory.py # Memory hội thoại
└── semantic_memory.py     # Memory ngữ nghĩa
```

### Flow

```
Input từ Tầng 1
    │
    ▼
┌─────────────────────────────────────┐
│  1. Intent Detection                │ ← Phân tích ý định
│     (question, code, search, etc.)  │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  2. Memory Integration              │ ← Nạp bộ nhớ
│     • Short-term: 5 tin nhắn gần    │
│     • Long-term: Tri thức đã học   │
│     • Working: Ngữ cảnh hiện tại   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  3. RAG Retrieval                   │ ← Tìm tài liệu
│     • Semantic Search (Vector)      │
│     • Keyword Search (SQLite FTS)   │
│     • Hybrid Search (RRF Fusion)    │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  4. Context Building                │ ← Xây dựng context
│     • System Prompt                 │
│     • Memory Context                │
│     • Knowledge Sources             │
│     • Conversation History          │
└─────────────────────────────────────┘
    │
    ▼
    Chuyển sang Tầng 3
```

### Memory Types

| Memory Type | Mô tả | TTL | Capacity |
|-------------|-------|-----|----------|
| Working | Ngữ cảnh task hiện tại | 1 giờ | 7 items |
| Short-term | Tin nhắn gần đây | 24 giờ | 100 items |
| Long-term | Tri thức đã học | Vĩnh viễn | 10,000 items |
| Conversation | Lịch sử chat | Vĩnh viễn | Unlimited |
| Semantic | Factual knowledge | Vĩnh viễn | 5,000 items |

### RAG Modes

| Mode | Algorithm | Use Case |
|------|-----------|----------|
| Semantic | Vector Cosine Similarity | Tìm kiếm ngữ nghĩa |
| Keyword | SQLite FTS5 | Tìm chính xác |
| Hybrid | Reciprocal Rank Fusion | Kết hợp cả hai |
| Code Similarity | Regex + TF-IDF | Tìm code |

---

## Tầng 3: LLM Core Engine (Transformer Architecture)

### Mục tiêu
- Tạo câu trả lời dựa trên context
- Sử dụng Transformer Architecture
- Streaming response

### Code Implementation

```
src/ke/llm/
├── manager.py             # Multi-provider LLM Manager
├── providers.py           # OpenAI, Anthropic, Gemini, Ollama, vLLM
└── client.py              # Legacy client

src/ke/cognitive/
└── engine.py              # Cognitive Engine (context → response)
```

### Transformer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRANSFORMER BLOCK                            │
│                                                                  │
│  Input Tokens                                                    │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────┐                                            │
│  │ Token Embedding │ ← Chuyển tokens thành vectors              │
│  └────────┬────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────┐                                            │
│  │ Positional      │ ← Thêm thông tin vị trí                   │
│  │ Encoding        │                                            │
│  └────────┬────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────┐                                            │
│  │ Self-Attention  │ ← Mối quan hệ giữa các từ                │
│  │ (Multi-Head)    │   "nó" → ám chỉ "con voi"                 │
│  └────────┬────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────┐                                            │
│  │ Feed Forward    │ ← Xử lý phi tuyến                        │
│  │ Network         │                                            │
│  └────────┬────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────┐                                            │
│  │ Layer Norm      │ ← Ổn định training                       │
│  └────────┬────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  Output: Probability Distribution                               │
│       (next token prediction)                                   │
└─────────────────────────────────────────────────────────────────┘
```

### LLM Providers

| Provider | Models | Streaming | Fallback |
|----------|--------|-----------|----------|
| OpenAI | GPT-4, GPT-3.5 | ✅ | Priority 100 |
| Anthropic | Claude 3 | ✅ | Priority 90 |
| Gemini | Gemini Pro | ✅ | Priority 80 |
| vLLM | Any model | ✅ | Priority 60 |
| Ollama | Llama 2, Mistral | ✅ | Priority 50 |
| Local | HF models | ❌ | Priority 10 |

### Autoregressive Generation

```
User: "What is machine learning?"

Step 1: [What] → predict "is"
Step 2: [What is] → predict "a"
Step 3: [What is a] → predict "branch"
Step 4: [What is a branch] → predict "of"
Step 5: [What is a branch of] → predict "AI"
... (continues until EOS token)

Each step: softmax(logits) → sample → append → repeat
```

---

## Tầng 4: Phản Hồi Real-time (Streaming & SSE)

### Mục tiêu
- Stream từng token về client
- Tạo cảm giác "gõ chữ" mượt mà
- Hiển thị sources ngay lập tức

### Code Implementation

```
src/ke/api/routers/
└── chat.py                # SSE Streaming endpoint

src/ke/cognitive/
└── engine.py              # Cognitive Engine (streaming)
```

### SSE Flow

```
Client (iOS/Web)
    │
    │ EventSource: /api/chat/stream
    │
    ▼
┌─────────────────────────────────────┐
│  Server-Sent Events (SSE)           │
│                                      │
│  data: {"type": "intent", ...}      │ ← Tầng 2: Intent
│  data: {"type": "memory", ...}      │ ← Tầng 2: Memory
│  data: {"type": "sources", ...}     │ ← Tầng 2: Sources
│  data: {"type": "token", "data": "M"}│ ← Tầng 3: Token 1
│  data: {"type": "token", "data": "a"}│ ← Tầng 3: Token 2
│  data: {"type": "token", "data": "ch"}│← Tầng 3: Token 3
│  ...                                 │
│  data: {"type": "done", ...}        │ ← Hoàn thành
│                                      │
└─────────────────────────────────────┘
    │
    ▼
Client renders tokens in real-time
```

### SSE Event Types

| Event Type | Mô tả | Timing |
|------------|-------|--------|
| `intent` | Kết quả phân tích ý định | ~10ms |
| `memory` | Context từ memory | ~50ms |
| `sources` | Tài liệu tìm thấy | ~100ms |
| `token` | Mỗi token từ LLM | ~50-200ms |
| `done` | Hoàn thành | - |

---

## So sánh với ChatGPT/Gemini/Claude

| Tính năng | ChatGPT | Gemini | Claude | Wcore X |
|-----------|---------|--------|--------|---------|
| Input Parsing | ✅ | ✅ | ✅ | ✅ |
| Guardrails | ✅ | ✅ | ✅ | ✅ |
| Memory | ✅ Limited | ✅ Limited | ✅ 200K | ✅ Unlimited |
| RAG | ✅ | ✅ | ✅ | ✅ Multi-mode |
| LLM | GPT-4 | Gemini Pro | Claude 3 | Multi-provider |
| Streaming | ✅ | ✅ | ✅ | ✅ SSE |
| Offline | ❌ | ❌ | ❌ | ✅ Local LLM |
| Self-hosted | ❌ | ❌ | ❌ | ✅ |

---

## Technology Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    TECHNOLOGY STACK                              │
│                                                                  │
│  Presentation Layer:                                            │
│  ├── iOS App: SwiftUI                                           │
│  ├── Web App: Next.js + Tailwind CSS                           │
│  └── CLI: Python Typer                                          │
│                                                                  │
│  API Gateway:                                                   │
│  ├── Framework: FastAPI                                         │
│  ├── Streaming: Server-Sent Events (SSE)                       │
│  ├── Auth: JWT + API Key (SHA-256)                             │
│  └── Rate Limit: Redis Sliding Window                          │
│                                                                  │
│  Cognitive Core:                                                │
│  ├── Intent Detection: Pattern matching                        │
│  ├── Memory: Multi-type (8 types)                              │
│  ├── RAG: Semantic + Keyword + Hybrid                          │
│  └── Reasoning: Chain-of-thought                               │
│                                                                  │
│  LLM Providers:                                                 │
│  ├── OpenAI (GPT-4/3.5)                                        │
│  ├── Anthropic (Claude 3)                                      │
│  ├── Google (Gemini)                                            │
│  ├── Ollama (Local)                                             │
│  └── vLLM (Self-hosted)                                        │
│                                                                  │
│  Storage:                                                       │
│  ├── Metadata: SQLite                                           │
│  ├── Vectors: ChromaDB (local + cloud)                         │
│  ├── Cache: Shelve                                              │
│  ├── Rate Limit: Redis                                          │
│  └── Chat History: ChromaDB Cloud                              │
│                                                                  │
│  Infrastructure:                                                │
│  ├── CI/CD: Codemagic                                           │
│  ├── iOS Build: Xcode                                           │
│  └── Deployment: Docker + Kubernetes                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Initialize knowledge base
ke init

# 3. Ingest knowledge
ke ingest ./documents/

# 4. Start API server with Redis
redis-server &
ke serve --port 8000

# 5. Generate API Key
curl -X POST http://localhost:8000/api/keys/generate \
  -H "Content-Type: application/json" \
  -d '{"name": "My App"}'

# 6. Chat with streaming
curl -X POST http://localhost:8000/api/chat/stream \
  -H "X-API-Key: wc_live_..." \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}' \
  -N  # Stream output
```

---

## Directory Structure

```
wadd-oss/
├── src/ke/                        # Backend (Python)
│   ├── api/                       # API Gateway
│   │   ├── server.py              # FastAPI server
│   │   ├── routers/               # API endpoints
│   │   └── middleware/            # Auth, Rate Limit
│   ├── auth/                      # Authentication
│   │   ├── generator.py           # API Key generation
│   │   ├── store.py               # Key storage (SQLite)
│   │   ├── middleware.py          # Auth middleware
│   │   └── rate_limiter.py        # Redis rate limiting
│   ├── cognitive/                 # Cognitive Core
│   │   ├── engine.py              # Main orchestrator
│   │   ├── memory_integration.py  # Memory management
│   │   ├── rag_pipeline.py        # RAG retrieval
│   │   └── intent_detector.py     # Intent detection
│   ├── llm/                       # LLM Providers
│   │   ├── manager.py             # Multi-provider manager
│   │   └── providers.py           # Provider implementations
│   ├── memory/                    # Memory System
│   │   ├── memory_manager.py      # Memory manager
│   │   ├── short_memory.py        # Short-term memory
│   │   ├── long_memory.py         # Long-term memory
│   │   └── conversation_memory.py # Conversation memory
│   ├── retrieval/                 # RAG Retrieval
│   │   ├── semantic.py            # Vector search
│   │   ├── keyword.py             # Keyword search
│   │   └── hybrid.py              # Hybrid search
│   ├── storage/                   # Data Storage
│   │   ├── metadata.py            # SQLite
│   │   ├── vector.py              # ChromaDB
│   │   ├── cloud.py               # ChromaDB Cloud
│   │   └── cache.py               # Shelve cache
│   └── domain/                    # Domain Models
│       ├── models.py              # Core models
│       └── interfaces.py          # Abstract interfaces
│
├── ios-app/                       # iOS App (SwiftUI)
│   └── KEApp/
│       ├── Views/                 # UI Views
│       └── Services/              # API Client
│
├── web-app/                       # Web App (Next.js)
│   ├── app/                       # Pages
│   └── components/                # React Components
│
├── codemagic.yaml                 # CI/CD Config
├── pyproject.toml                 # Python Config
└── ARCHITECTURE.md                # This file
```
