# 💊 HCP CRM — AI-First Healthcare Professional Interaction Module

An AI-powered CRM system for pharmaceutical field sales representatives to log, manage, and analyze HCP (Healthcare Professional) interactions using both structured forms and a conversational AI chat interface.

---

## 🎯 Project Overview

Field reps can log HCP interactions in **two ways**:
1. **Structured Form** — Fill in fields manually (HCP name, specialty, products, etc.)
2. **AI Chat Interface** — Type naturally, and the LangGraph agent extracts, summarizes, and saves the interaction automatically

Both methods persist data to PostgreSQL and provide AI-generated summaries, sentiment analysis, and follow-up suggestions.

---

## 🧱 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React.js + Redux Toolkit |
| Backend | Python FastAPI |
| AI Agent | LangGraph |
| LLM | Groq API — `gemma2-9b-it` (primary), `llama-3.3-70b-versatile` (fallback) |
| Database | PostgreSQL |
| Font | Google Inter |

---

## 📁 Project Structure

```
hcp-crm/
├── backend/
│   ├── app/
│   │   ├── config.py                  # Settings & env vars
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── database/
│   │   │   └── connection.py          # SQLAlchemy engine & session
│   │   ├── models/
│   │   │   └── interaction.py         # ORM model
│   │   ├── schemas/
│   │   │   └── interaction.py         # Pydantic schemas
│   │   ├── services/
│   │   │   └── interaction_service.py # CRUD service layer
│   │   ├── routes/
│   │   │   ├── interactions.py        # REST endpoints
│   │   │   └── chat.py                # Chat endpoint
│   │   └── langgraph_agent/
│   │       ├── llm_service.py         # Groq LLM wrapper
│   │       ├── tools.py               # 5 LangGraph tools
│   │       └── agent.py               # LangGraph graph & runner
│   ├── schema.sql                     # Raw SQL schema
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── public/
    │   └── index.html
    └── src/
        ├── App.js
        ├── index.js
        ├── services/
        │   └── api.js                 # Axios client
        ├── store/
        │   ├── index.js               # Redux store
        │   └── slices/
        │       ├── interactionsSlice.js
        │       ├── chatSlice.js
        │       └── dashboardSlice.js
        ├── components/
        │   ├── Sidebar.js
        │   ├── InteractionForm.js
        │   ├── ChatInterface.js
        │   └── InteractionTable.js
        └── pages/
            ├── Dashboard.js
            └── LogInteraction.js
```

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- A [Groq API key](https://console.groq.com)

---

### 1. Database Setup

```bash
# Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE hcp_crm;"

# Run schema (optional — tables auto-create on startup)
psql -U postgres -d hcp_crm -f backend/schema.sql
```

---

### 2. Backend Setup

```bash
cd hcp-crm/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set your values:
#   GROQ_API_KEY=your_key_here
#   DATABASE_URL=postgresql://postgres:password@localhost:5432/hcp_crm
```

#### `.env` file:
```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/hcp_crm
PRIMARY_MODEL=gemma2-9b-it
FALLBACK_MODEL=llama-3.3-70b-versatile
```

#### Start the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

---

### 3. Frontend Setup

```bash
cd hcp-crm/frontend

# Install dependencies
npm install

# Start development server
npm start
```

App available at: http://localhost:3000

---

## 🔑 Groq API Key Setup

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up / log in
3. Navigate to **API Keys** → **Create API Key**
4. Copy the key and paste it in `backend/.env` as `GROQ_API_KEY`

The system uses `gemma2-9b-it` as the primary model and automatically falls back to `llama-3.3-70b-versatile` on failure.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/interactions/log-interaction` | Log interaction via form |
| `GET` | `/api/interactions/` | Get all interactions |
| `GET` | `/api/interactions/{id}` | Get single interaction |
| `GET` | `/api/interactions/interactions/{hcp_name}` | Get by HCP name |
| `PUT` | `/api/interactions/edit-interaction/{id}` | Update interaction |
| `DELETE` | `/api/interactions/{id}` | Delete interaction |
| `GET` | `/api/interactions/dashboard/stats` | Dashboard statistics |
| `POST` | `/api/chat/` | AI chat endpoint |
| `GET` | `/health` | Health check |

---

## 🤖 LangGraph Agent Tools

| Tool | Description |
|------|-------------|
| `LogInteractionTool` | Extracts entities from text, generates summary, saves to DB |
| `EditInteractionTool` | Fetches and updates an existing interaction |
| `GetInteractionHistoryTool` | Returns sorted interaction history for an HCP |
| `SuggestNextActionTool` | AI-powered follow-up strategy suggestions |
| `SummarizeInteractionsTool` | Comprehensive summary with trends and sentiment |

---

## 📊 Database Schema

```sql
CREATE TABLE interactions (
    id                SERIAL PRIMARY KEY,
    hcp_name          VARCHAR(255) NOT NULL,
    specialty         VARCHAR(255),
    hospital          VARCHAR(255),
    interaction_type  VARCHAR(50),       -- Visit / Call / Meeting
    datetime          TIMESTAMPTZ,
    products          TEXT,
    notes             TEXT,
    summary           TEXT,              -- AI-generated
    sentiment         VARCHAR(50),       -- positive / neutral / negative
    follow_up_date    TIMESTAMPTZ,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🚀 Running Both Services

Open two terminals:

**Terminal 1 — Backend:**
```bash
cd hcp-crm/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd hcp-crm/frontend
npm start
```

Then open http://localhost:3000

---

## 🧪 Example Chat Inputs

```
"Met Dr. Priya Rao at Apollo Hospital today. Discussed Januvia and Metformin XR for diabetes management. She was very interested and asked for clinical trial data. Follow up next Monday."

"Called Dr. Arjun Mehta about Rosuvastatin. He was busy but agreed to a meeting next week."

"Show me interaction history for Dr. Rao"

"Suggest next actions for Dr. Mehta"

"Summarize all interactions with Dr. Sunita Sharma"
```
