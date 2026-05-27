# AIVOA.AI — Interview Shortlist Letter + Complete Project Explanation

---

Hello Candidate,

Thank you for applying to **AIVOA.AI**. We are pleased to inform you that you have been shortlisted for the next stage of the selection process.

Before proceeding to the final interview round, a pre-screening telephonic interview will be conducted on **1st May between 10:00 AM and 3:00 PM**. Please ensure that you are available during this time window to attend the call.

The interview will be based on the assignment you have submitted and will focus on the following:

**Task 1:**
- Complete technical understanding of your code implementation
- End-to-end clarity of the solution
- No theoretical definitions will be asked — only practical understanding and reasoning

**Task 2:**
- In-depth understanding of the domain (QMS module)
- Discussion based on examples such as API (Active Pharmaceutical Ingredient) or FDF
- Focus will be on practical knowledge and your domain research rather than definitions
- If you have not received the assignment document or have not attempted Task 2 yet, please let us know. We can provide additional time for preparation

**Note:** You will be pre-screened completely based on your understanding of code implementation (Task 1) and domain understanding (Task 2). Kindly go through the assignment thoroughly and ensure a clear understanding. Only those shortlisted in the pre-screening will move ahead to the next stage of the process.

Additionally, please confirm if you are comfortable with the offered salary/stipend range of **₹8,000 to ₹15,000 per month**.

Kindly confirm your availability for the interview. If you have any questions or need clarification, feel free to reach out.

Thank you.

**Best regards,**
Team AIVOA.AI

---
---

# 📘 COMPLETE PROJECT EXPLANATION — POINT BY POINT

> Read this fully before the interview. Every point below is something you must be able to explain out loud, with examples, without reading.

---

## POINT 1 — WHAT IS THIS PROJECT?

This project is an **AI-first CRM (Customer Relationship Management) system** built for **pharmaceutical field sales representatives**.

- A pharma sales rep visits doctors (called HCPs — Healthcare Professionals) every day
- After each visit they must record: which doctor they met, which hospital, which drug was discussed, how the doctor reacted, and when to follow up
- Traditional CRM = manual form filling = slow, boring, often skipped
- This AI CRM = rep just types naturally like a WhatsApp message → AI does everything automatically

**One line answer:** "I built a system where pharma reps can log doctor interactions either by filling a form OR by just chatting with an AI in plain English."

---

## POINT 2 — WHAT ARE THE TWO WAYS TO LOG AN INTERACTION?

### Way 1 — Structured Form
- Rep fills fields manually: Doctor name, Hospital, Specialty, Products discussed, Notes, Follow-up date
- Clicks Submit → data goes directly to PostgreSQL database
- No AI involved here — clean, fast, direct save

### Way 2 — AI Chat Interface
- Rep types: *"Met Dr. Rao at Apollo Hospital. Discussed Januvia for diabetes. She was very interested. Follow up next Monday."*
- This goes to the AI agent
- AI reads it, extracts all the fields automatically, saves to database
- AI also generates a summary, detects sentiment (positive/neutral/negative), and suggests follow-up actions

**Why two ways?** Some reps prefer forms. Some prefer talking. Both save to the same database.

---

## POINT 3 — WHAT IS THE TECH STACK AND WHY EACH ONE?

| Technology | What it does | Why I chose it |
|-----------|-------------|----------------|
| **React** | Frontend UI | Component-based, fast rendering, industry standard |
| **Redux** | State management | Centralized store — when chat saves data, table updates automatically |
| **FastAPI** | Backend API | Async support for LLM calls, auto Swagger docs, Pydantic validation built-in |
| **LangGraph** | AI agent orchestration | Routes to correct tool, maintains state, modular |
| **Groq API** | LLM provider | Runs gemma2-9b-it model at very high speed, free tier available |
| **gemma2-9b-it** | The AI brain | Extracts entities, detects sentiment, generates summaries |
| **PostgreSQL** | Database | Robust, production-grade, supports complex queries |
| **SQLAlchemy** | ORM | Maps Python classes to DB tables, no raw SQL needed |
| **Pydantic** | Validation | Validates every API request and response automatically |

---

## POINT 4 — WHAT IS LANGGRAPH AND WHY IS IT USED?

**LangGraph** is a framework for building AI agents as a **directed graph** (like a flowchart).

- **Node** = one action (classify intent, call a tool, generate response)
- **Edge** = connection between actions
- **State** = shared data that flows through all nodes

### Why not just call the LLM directly?

If I called the LLM directly, I could only do one thing. But users might want to:
- Log a new interaction
- Edit an existing one
- See history for a doctor
- Get suggestions for next steps
- Get a summary of all visits

LangGraph lets me **classify the intent first**, then **route to the correct tool**. It's like a smart switchboard.

### The Graph Flow:

```
User types message
       ↓
Node 1: classify_intent  ← LLM decides what user wants
       ↓
Conditional Edge: route_to_tool  ← picks the right path
       ↓
Node 2: execute_correct_tool  ← does the actual work
       ↓
END → response sent back to user
```

---

## POINT 5 — WHAT ARE THE 5 LANGGRAPH TOOLS?

### Tool 1 — LogInteractionTool
- **What it does:** Takes the user's natural language text, sends it to the LLM, gets back structured JSON, saves to database
- **Input:** "Met Dr. Rao at Apollo. Discussed Januvia. She was interested."
- **Output:** Saves record with hcp_name="Dr. Rao", hospital="Apollo", products="Januvia", sentiment="positive"

### Tool 2 — EditInteractionTool
- **What it does:** Finds an existing interaction by ID and updates specific fields
- **Input:** "Edit interaction 5, change follow-up to next Friday"
- **Output:** Updated record in database

### Tool 3 — GetInteractionHistoryTool
- **What it does:** Fetches all past interactions for a specific doctor from the database
- **Input:** "Show me history for Dr. Priya Rao"
- **Output:** List of all interactions with that doctor, sorted by date

### Tool 4 — SuggestNextActionTool
- **What it does:** Looks at the most recent interaction and uses LLM to suggest what the rep should do next
- **Input:** Latest interaction data for Dr. Mehta
- **Output:** ["Call within 7 days", "Send clinical trial data", "Invite to webinar"]

### Tool 5 — SummarizeInteractionsTool
- **What it does:** Fetches ALL interactions with a doctor and generates a comprehensive AI analysis
- **Input:** All 8 visits with Dr. Sharma
- **Output:** Trend analysis, sentiment breakdown, opportunities, risk alerts

---

## POINT 6 — HOW DOES CHAT BECOME STRUCTURED DATA? (Most Important)

This is the core of the project. Step by step:

**Step 1:** User types in chat box:
> "Met Dr. Rao at Apollo Hospital today. Discussed Januvia for diabetes. She was very interested and asked for samples. Follow up next Monday."

**Step 2:** React sends this to backend:
```
POST /api/chat/
{ "message": "Met Dr. Rao at Apollo..." }
```

**Step 3:** FastAPI receives it, calls `run_agent(message, db)`

**Step 4:** LangGraph starts. Node 1 (classify_intent) sends message to LLM:
> "What does the user want to do? Options: log_interaction, edit_interaction, get_history, suggest_actions, summarize"
> LLM replies: "log_interaction"

**Step 5:** Conditional edge routes to `execute_log_interaction` node

**Step 6:** This node calls `log_interaction_tool()` which calls `extract_interaction()` on the LLM with this prompt:
> "Extract these fields and return ONLY valid JSON: hcp_name, hospital, specialty, interaction_type, products, sentiment, follow_up_date, summary"

**Step 7:** LLM returns:
```json
{
  "hcp_name": "Dr. Rao",
  "hospital": "Apollo Hospital",
  "products": "Januvia",
  "sentiment": "positive",
  "interaction_type": "Visit",
  "follow_up_date": null,
  "summary": "Productive visit with Dr. Rao at Apollo Hospital..."
}
```

**Step 8:** Python parses this JSON, creates a database record using SQLAlchemy, saves to PostgreSQL

**Step 9:** LLM is called again to suggest follow-up actions

**Step 10:** Response goes back: FastAPI → Redux → UI shows the extracted data card + suggestions

**If JSON parsing fails:** Raw text is saved as notes — no data is ever lost

---

## POINT 7 — WHAT IS THE DATABASE SCHEMA?

Table name: **interactions**

| Column | Type | What it stores |
|--------|------|----------------|
| id | SERIAL | Auto-increment primary key |
| hcp_name | VARCHAR(255) | Doctor's full name |
| specialty | VARCHAR(255) | Cardiology, Endocrinology, etc. |
| hospital | VARCHAR(255) | Apollo, AIIMS, Fortis, etc. |
| interaction_type | VARCHAR(50) | Visit / Call / Meeting |
| datetime | TIMESTAMPTZ | When the interaction happened |
| products | TEXT | Drug names discussed |
| notes | TEXT | Rep's raw notes |
| summary | TEXT | AI-generated professional summary |
| sentiment | VARCHAR(50) | positive / neutral / negative |
| follow_up_date | TIMESTAMPTZ | Next scheduled contact date |
| created_at | TIMESTAMPTZ | When record was created |
| updated_at | TIMESTAMPTZ | When record was last modified |

**Why `summary` and `sentiment` are separate columns:** These are AI-generated fields. The LLM reads the notes and produces these automatically. They are stored so we don't need to call the LLM again every time we display the data.

---

## POINT 8 — WHAT IS THE FRONTEND STRUCTURE?

### Pages:
1. **Dashboard** — Shows total interactions, sentiment breakdown bar, upcoming follow-ups count, recent 5 interactions
2. **Log Interaction** — The main screen with two tabs: Structured Form + AI Chat
3. **QMS Domain** — Pharma quality management guide (Deviation, CAPA, Change Control, Audit, API vs FDF)
4. **Interview Guide** — Q&A preparation page

### Redux Store has 3 slices:
1. **interactionsSlice** — Stores the list of all interactions, handles CRUD operations
2. **chatSlice** — Stores chat messages array, loading state, extracted data from AI
3. **dashboardSlice** — Stores dashboard statistics

### Why Redux?
When a user logs an interaction via chat, BOTH the chat messages AND the interactions table need to update at the same time. Redux makes this easy — one action can trigger updates across multiple components.

---

## POINT 9 — WHAT ARE THE API ENDPOINTS?

| Method | URL | What it does |
|--------|-----|-------------|
| POST | /api/interactions/log-interaction | Save form data to DB |
| GET | /api/interactions/ | Get all interactions |
| GET | /api/interactions/{id} | Get one interaction |
| GET | /api/interactions/interactions/{hcp_name} | Get by doctor name |
| PUT | /api/interactions/edit-interaction/{id} | Update an interaction |
| DELETE | /api/interactions/{id} | Delete an interaction |
| GET | /api/interactions/dashboard/stats | Get dashboard numbers |
| POST | /api/chat/ | Send message to AI agent |
| GET | /health | Check if server + DB are running |

---

## POINT 10 — WHAT CHALLENGES DID YOU FACE?

### Challenge 1 — LangGraph Serialization Error
**Problem:** I put the database session (SQLAlchemy Session) inside the LangGraph state. LangGraph tries to serialize (convert to JSON) the state at each step. A database session has open connections and locks — it cannot be converted to JSON.

**Error:** `Object of type Session is not JSON serializable`

**Fix:** I removed `db` from the state completely. Instead, I pass `db` into `build_agent_graph(db)` and each node captures it via Python closure. The graph is built fresh for each request. The db is available inside each node but never stored in the state.

### Challenge 2 — Database URL with Special Character
**Problem:** My PostgreSQL password was `Radha@123`. The `@` symbol in the password broke the URL parser. It read `123@localhost` as the hostname instead of `localhost`.

**Error:** `could not translate host name "123@localhost" to address`

**Fix:** URL-encode the `@` as `%40`:
`postgresql://postgres:Radha%40123@localhost:5432/hcp_crm`

### Challenge 3 — Pydantic v2 Compatibility
**Problem:** Using `Field(None, description="...")` on `Optional[datetime]` fields throws a schema generation error in Pydantic v2.

**Fix:** Use plain `Optional[datetime] = None` without `Field()` for optional fields. Only use `Field()` when you need validation constraints like `min_length`.

---

## POINT 11 — HOW DOES THE DASHBOARD WORK?

The dashboard calls `GET /api/interactions/dashboard/stats` which runs these SQL queries:

1. `COUNT(*)` — total interactions
2. `COUNT(*) WHERE sentiment = 'positive'` — positive count
3. `COUNT(*) WHERE sentiment = 'negative'` — negative count
4. `COUNT(*) WHERE sentiment = 'neutral'` — neutral count
5. `COUNT(*) WHERE follow_up_date >= NOW()` — upcoming follow-ups
6. `SELECT * ORDER BY created_at DESC LIMIT 5` — recent 5 interactions

All of this is returned in one API call and displayed as stat cards, a sentiment bar, and a recent interactions list.

---

## POINT 12 — HOW DOES THE GROQ LLM SERVICE WORK?

The `GroqLLMService` class has 4 methods:

1. **`extract_interaction(text)`** — Sends text to LLM with a prompt asking for structured JSON. Parses the JSON response. If parsing fails, returns raw text as notes.

2. **`suggest_next_actions(interaction_data)`** — Sends interaction data to LLM asking for 3-5 actionable next steps. Returns a list of strings.

3. **`summarize_interactions(interactions_list)`** — Sends all interactions for an HCP to LLM asking for trend analysis, sentiment arc, opportunities, and risk alerts.

4. **`understand_intent(message)`** — Sends user message to LLM asking it to classify the intent into one of 5 categories.

**Fallback:** If `gemma2-9b-it` fails, it automatically retries with `llama-3.3-70b-versatile`.

**Lazy initialization:** The Groq client is created only when first needed (not at import time) so the API key is always read from the `.env` file correctly.

---

## POINT 13 — END TO END FLOW (Say This in Interview)

> "User opens the app → sees Dashboard with all stats → clicks Log Interaction → chooses AI Chat tab → types a natural language description of their doctor visit → React sends it to FastAPI backend → FastAPI calls the LangGraph agent → agent's first node classifies the intent using the LLM → conditional edge routes to the LogInteractionTool node → that tool calls the LLM again to extract structured data → LLM returns JSON with doctor name, hospital, products, sentiment, summary → Python saves this to PostgreSQL using SQLAlchemy → agent calls LLM one more time to generate follow-up suggestions → all results flow back through FastAPI → Redux updates the chat messages and the interactions table → user sees the AI response with extracted data card and suggested actions."

---

## POINT 14 — TASK 2: QMS DOMAIN EXPLANATION

### What is QMS?
Quality Management System — the set of processes that ensure pharma products are made correctly and safely. Regulated by FDA (USA), EMA (Europe), CDSCO (India).

### Deviation — What it is and example
A deviation is when something goes wrong during manufacturing — any departure from the approved procedure.

**Example:** SOP says maintain reactor temperature at 80°C. Actual temperature went to 85°C for 15 minutes.
- This is an **unplanned deviation**
- The batch gets quarantined
- An investigation starts
- Root cause found: cooling valve malfunction
- CAPA is raised

### CAPA — What it is and example
CAPA = Corrective and Preventive Action.
- **Corrective** = fix the current problem (replace the valve, retest the batch)
- **Preventive** = stop it happening again (install alarm at 78°C, add to maintenance schedule, update SOP)
- After 30 days, an effectiveness check confirms it worked

### Change Control — What it is and example
Any change to a validated process must go through formal approval.

**Example:** Company wants to switch API supplier to save cost.
- Impact assessment: Will it affect quality? YES → needs regulatory filing
- Technical evaluation: Audit new supplier, run comparative tests, stability studies
- Approval from QA Head + Regulatory Affairs + Production Head
- Only implement after regulatory approval
- Monitor 3 batches after change
- Then close the change control

### API vs FDF
- **API** = Active Pharmaceutical Ingredient = the raw drug molecule
  - Example: Metformin powder, Atorvastatin crystals, Sitagliptin
- **FDF** = Finished Dosage Form = what the patient actually takes
  - Example: Metformin 500mg tablet, Lipitor 10mg capsule, Januvia 100mg tablet

**Connection to CRM:** When a sales rep visits Dr. Rao and discusses "Januvia" — Januvia is the FDF (brand name tablet). Sitagliptin is the API inside it. The CRM logs the FDF name for commercial tracking. If Dr. Rao reports a side effect, QMS traces it back to the API batch number.

---

## POINT 15 — QUICK ANSWERS FOR COMMON INTERVIEW QUESTIONS

**Q: Why LangGraph?**
> "Because I needed to handle multiple intents — log, edit, history, suggest, summarize. LangGraph lets me classify intent first and route to the correct tool. A direct LLM call can only do one thing."

**Q: How does chat become structured data?**
> "The user's text goes to the LLM with a system prompt asking for specific JSON fields. The LLM extracts hcp_name, hospital, products, sentiment, summary and returns JSON. I parse it and save to PostgreSQL."

**Q: Why FastAPI?**
> "Async support for LLM calls, auto Swagger docs at /docs, and Pydantic validation built-in. Flask would block on every LLM call."

**Q: Why Redux?**
> "When chat saves an interaction, both the chat state and the interactions table need to update simultaneously. Redux makes cross-component updates easy."

**Q: What is a Deviation?**
> "Any departure from an approved procedure. Example: temperature exceeded limit during API manufacturing. Must be documented, investigated, and a CAPA raised."

**Q: What is CAPA?**
> "Corrective action fixes the current problem. Preventive action stops it from happening again. Always linked to a deviation or audit finding."

**Q: API vs FDF?**
> "API is the raw drug molecule like Metformin powder. FDF is the final product like Metformin 500mg tablet. API manufacturer focuses on purity and synthesis. FDF manufacturer focuses on formulation and stability."

---

## FINAL CHECKLIST BEFORE INTERVIEW

- [ ] Can explain the full end-to-end flow without looking at notes
- [ ] Can explain what LangGraph is and why it was used
- [ ] Can explain how chat text becomes database records
- [ ] Can name all 5 tools and what each one does
- [ ] Can explain the database schema and why each column exists
- [ ] Can explain the 3 challenges faced and how they were solved
- [ ] Can explain Deviation with a real example
- [ ] Can explain CAPA with corrective vs preventive difference
- [ ] Can explain Change Control with the supplier change example
- [ ] Can explain API vs FDF with product examples
- [ ] Comfortable with ₹8,000 to ₹15,000 per month range

---

*All the best for your interview on 1st May! You built this — you know it better than anyone.*
