# margin-agent

An agentic system that automates supplier invoice dispute handling for retail promotion margin recovery. Built from scratch in raw Python — no agent frameworks — to understand the core concepts of agentic AI systems.

---

## What This Does

Tesco raises invoices to suppliers based on promotional sales. Suppliers sometimes dispute these invoices. This system automates the analysis and response process that was previously handled manually by the Margin Discovery (MD) team.

```
Supplier disputes invoice
        ↓
Supervisor Agent reads email + loads supplier knowledge
        ↓
Analyst Agent queries DB, analyses dispute
        ↓
Supervisor decides outcome
        ↓
CORRECT        → explanation email sent to supplier
WRONG          → escalation report sent to MD team
NOT_CONCLUSIVE → full report escalated to MD team
        ↓
Knowledge graph updated for future disputes
```

---

## Architecture

```
margin-agent/
├── main.py                        # entry point
├── config.py                      # all constants — model, tokens, paths
├── knowledge_graph.py             # supplier-category knowledge graph
│
├── agents/
│   ├── supervisor.py              # orchestrator — manages full lifecycle
│   └── analyst.py                 # analyst — queries DB, returns findings
│
├── clients/
│   ├── supabase_client.py         # supabase connection
│   └── claude_client.py           # anthropic client
│
├── tools/
│   ├── db_tools.py                # supabase query functions
│   ├── mail_tools.py              # mock email read/send
│   └── memory_tools.py            # .md file memory handler
│
├── conversation.py                # core agent loop engine
│
├── memory/
│   ├── active_tickets/            # live dispute tickets — one .md per calc_id
│   └── archive/                   # supplier knowledge graphs
│
├── mock_emails/
│   ├── dispute_001.json           # S1 — correct calculation
│   ├── dispute_002.json           # S2 — wrong rate
│   ├── dispute_003.json           # S3 — parent/subsidiary mismatch
│   ├── dispute_004.json           # S4 — not conclusive
│   └── sent/                      # outbound emails written here
│
├── db/
│   ├── schema.sql                 # all table definitions
│   └── seed.sql                   # test data for all 4 scenarios
│
├── notebooks/
│   ├── 01_conversation_loop.ipynb
│   ├── 02_analyst_agent.ipynb
│   ├── 03_supervisor_agent.ipynb
│   └── 04_knowledge_graph.ipynb
│
└── app.py                         # streamlit UI
```

---

## Core Concepts Implemented

### 1. Tool Use
Claude cannot call Supabase directly. It calls named tools you define. You control exactly what it can access.

```python
# Claude decides to call this
get_calculation(calculation_id="YCCP-41")

# db_tools.py executes it, returns data
# Claude reasons over the result
```

### 2. Agent Loop
The heartbeat of every agent. Runs until Claude stops calling tools or max turns hit.

```python
while turn < max_turns:
    response = client.messages.create(...)

    if response.stop_reason == "end_turn":
        break

    if response.stop_reason == "tool_use":
        # execute tools, feed results back
        messages.append(tool_results)
        turn += 1
```

### 3. Multi-Agent — Sequential Pipeline
Supervisor orchestrates Analyst. Each agent owns its own tools, system prompt, and tool executor. Same `run_conversation_loop` engine powers both.

```
supervisor_tool_executor  →  read_ticket, send_email
analyst_tool_executor     →  get_calculation, get_sales_breakdown,
                             get_agreement, get_supplier,
                             execute_analyst_query
```

### 4. File-Based Memory
Every active dispute has a `.md` ticket file. Agents read and write sections as the dispute progresses. Inspectable and debuggable.

```
memory/active_tickets/YCCP-41.md

# Ticket: YCCP-41
status: open
loop_count: 0

## Dispute
[supplier email body]

## Analyst Findings
[written by analyst agent]

## Supervisor Notes
[written by supervisor agent]

## Thread
[conversation history]
```

### 5. Knowledge Graph
Persistent supplier-category memory. Grows richer with every resolved dispute. LLM detects patterns and updates strategy notes automatically.

```
memory/archive/DIAGEO-GREAT-BRITAIN-LIMITED-Beers-Wines-Spirits.md

## Dispute Patterns
- Consistently disputes volume — claims fewer units than recorded
- Has never successfully disputed a calculation

## Agent Notes
- Lead with sales breakdown — Diageo accepts hard numbers
- Reference previous disputes explicitly
```

### 6. Context Management
Two layers of compression prevent token bloat across long sessions.

- **API level** — Anthropic server-side clearing of old tool results
- **File level** — ticket files compressed by Claude when they exceed 7,500 words

### 7. Human-in-the-Loop
Wrong calculation path flags for human approval before any DB write. Agent pauses, human corrects, agent resumes.

---

## Data Model

Six tables in Supabase (PostgreSQL):

| Table | Purpose |
|---|---|
| `suppliers` | Master list with parent/subsidiary self-reference |
| `products` | Product master — one row per TPNB |
| `promotions` | Promotion windows and types |
| `agreements` | Agreed funding rates per promotion + supplier + product |
| `sales` | Weekly actual sales at tpnb + supplier grain |
| `calculations` | Output of calculation engine — one row per invoice line |

### Key Business Rule — Parent/Subsidiary
A subsidiary sells at Tesco but the invoice goes to the parent. The `main_subsidiary_alternate` column in calculations controls this. Most common source of disputes.

```sql
-- Invoice goes to parent when subsidiary sells
CASE
    WHEN sup.supplier_type = 'Subsidiary'
    THEN sup.parent_supplier_number
    ELSE s.sales_supplier
END AS funded_supplier_number
```

### Core Calculation
```
total_funding = promo_sales_volume × supplier_promotion_funding_per_unit
```

---

## Test Scenarios

| ID | Calc | Supplier | Dispute type | Expected outcome |
|---|---|---|---|---|
| S1 | YCCP-41 | Diageo | Volume — claims 8, DB shows 10 | CORRECT → explanation email |
| S2 | YCCP-44 | Colgate | Rate — DB has £0.20, contract says £0.25 | WRONG → MD team escalation |
| S3 | YCCP-43 | Diageo | Wrong entity — subsidiary disputes parent invoice | CORRECT → parent/sub explanation |
| S4 | YCCP-47 | Unilever | Cancelled promo — supplier claims it was cancelled | NOT_CONCLUSIVE → MD team |

---

## Setup

### Prerequisites
```
Python 3.11+
Supabase account (free tier)
Anthropic API key
```

### Install
```bash
git clone https://github.com/your-username/margin-agent
cd margin-agent
pip install -r requirements.txt
```

### Environment
```bash
# .env
ANTHROPIC_API_KEY=your_key_here
SUPABASE_URL=your_url_here
SUPABASE_ANON_KEY=your_key_here
```

### Database
```bash
# Run in Supabase SQL editor in order
1. schema.sql
2. seed.sql
3. run_calculation.sql   # populates calculations table for week 202603
```

### Run
```bash
# CLI
python main.py dispute_001

# UI
streamlit run app.py
```

---

## Requirements

```
anthropic
supabase
python-dotenv
streamlit
```

---

## What's Not Built Yet

- Inter-agent loop — supervisor calling analyst multiple times dynamically
- Supplier reply loop — processing follow-up emails from suppliers
- NL→SQL integration — plugging in existing RAG-based query tool
- Real email integration — replacing mock JSON files with actual inbox
- Human approval UI — proper interface for MD team to approve DB corrections
- Vector store — for cross-supplier semantic search at scale

---

## Learning Objectives

This project was built to understand the following agent concepts hands-on:

- Tool use and tool boundaries
- The agent loop — stop_reason, message history, max_turns
- Multi-agent orchestration — supervisor + analyst pattern
- File-based persistent memory
- Context window management
- Human-in-the-loop interrupts
- Prompt engineering for structured agent output
- Knowledge graph with LLM-driven pattern detection

Built without LangGraph or CrewAI — every concept implemented explicitly in raw Python.