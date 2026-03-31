## FLow

[Tesco Invoice System]
↓
[Supplier_Mail] 
↓
[Accept] ─→ [Deal raised: NAR]
[Dispute/query]  
↓
[Superviser_Agent]---query ─→[Analyst_Agent] --> [Superviser_Agent] loop till 5 times
↓
[Analysis result]
↓
[Correct] ─→ [mail to supplier eith details attached] -> [mail 2]-> [supplier ok, loop closed, not ok loop starts] 
[Wrong]─→ [Send the details to human so can corrct the entry] -> [human updated and confirm, update goes to Superviser_Agent -> [mail sent to supplier]
[Not_Conclusive] ─→ [Send the Analysis report to human so cn take forward] ->[loop closed]


## memory
- create a memory folder like this - https://github.com/anthropics/claude-cookbooks/blob/main/tool_use/memory_cookbook.ipynb
- craete a active ticket folder inside memory. .md file every calculation_id. Analyst agent and superviser agent will write here the details.
    - Details to keep : suppier id, loop number, calculation id, Analysis agent will query and keep a row with detailed column from the db.
    - Compression if context increases 10k tokens.
- At close of every ticket, maintain a summary of every ticket inside a .md file for every supplier-category level. Ex - Colgate-Household. Can get these in the invoice.It will help teh agent see the previvous issues and how to solve it.

## Project Structure
margin-agent/
│
margin-agent/
├── .env
├── main.py                  # Entry point + agent loop
├── agents/
│   ├── supervisor.py        # Supervisor — orchestration + LLM calls
│   └── analyst.py           # Analyst — SQL tools + LLM calls
├── tools/
│   ├── db_tools.py          # Supabase queries
│   ├── mail_tools.py        # Mock send/read email
│   └── memory_tools.py      # Read/write/compress .md tickets
├── memory/
│   ├── active_tickets/      # YCCP-41.md ...
│   └── archive/             # Colgate-Household.md ...
└── mock_emails/
    └── dispute_001.json