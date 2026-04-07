SUPERVISOR_SYSTEM_PROMPT = """
You are the Supervisor Agent for Tesco's Margin Discovery team.

Your job is to manage supplier invoice disputes end to end.

You will receive:
- A supplier dispute email
- An analysis result from the Analyst Agent (CORRECT/WRONG/NOT_CONCLUSIVE)
- The active ticket context

## Your Decision Rules

CORRECT calculation:
- Read the analyst findings from the ticket
- Draft a professional explanation email to the supplier
- Include exact numbers — volume, rate, total funding
- Send the email using send_email tool
- Update ticket status to "explanation_sent"

WRONG calculation:
- Draft a detailed correction report with exact delta
- Send to MD team using send_email tool
- Include: what is wrong, what it should be, calculation_id
- Update ticket status to "awaiting_human"

NOT_CONCLUSIVE:
- Draft full analysis report for MD team
- Include everything the analyst found
- Send to MD team using send_email tool
- Update ticket status to "escalated"

## Rules
- Always read the ticket first before acting
- Always update the ticket after acting
- Be professional in all emails
- Always include calculation_id in every email subject
"""

SUPERVISOR_TOOLS = [
    {
        "name": "read_ticket",
        "description": "Read the active dispute ticket for context.",
        "input_schema": {
            "type": "object",
            "properties": {
                "calculation_id": {
                    "type": "string",
                    "description": "e.g. YCCP-41"
                }
            },
            "required": ["calculation_id"]
        }
    },
    {
        "name": "update_ticket",
        "description": "Update a section in the active dispute ticket.",
        "input_schema": {
            "type": "object",
            "properties": {
                "calculation_id": {
                    "type": "string"
                },
                "section": {
                    "type": "string",
                    "description": "Section to update: Supervisor Notes or Thread"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write"
                }
            },
            "required": ["calculation_id", "section", "content"]
        }
    },
    {
        "name": "send_email",
        "description": "Send an email to supplier or MD team.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient email"
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject"
                },
                "body": {
                    "type": "string",
                    "description": "Email body"
                },
                "calculation_id": {
                    "type": "string"
                }
            },
            "required": ["to", "subject", "body", "calculation_id"]
        }
    }
]

from tools.mail_tools import send_email
from tools.memory_tools import MemoryToolHandler
from config import MEMORY_BASE_PATH
from datetime import datetime, timezone
from utils.conversation import run_conversation_loop
from clients.claude_client import get_claude_client
from agents.analyst import run_analyst
from config import MODEL, MAX_TOKENS, MAX_AGENT_TURNS
from datetime import datetime, timezone
from utils.knowledge_graph import _read_knowledge_graph, _update_knowledge_graph
from tools.db_tools import get_calculation
import textwrap

memory = MemoryToolHandler(base_path=MEMORY_BASE_PATH)

def supervisor_tool_executor(tool_name: str, tool_input: dict) -> str:
    try:
        if tool_name == "read_ticket":
            result = memory.execute(
                command="view",
                path=f"/memories/active_tickets/{tool_input['calculation_id']}.md"
            )
            return result.get("success") or result.get("error")

        elif tool_name == "update_ticket":
            calculation_id = tool_input["calculation_id"]
            section = tool_input["section"]
            content = tool_input["content"]

            result = memory.execute(
                command="str_replace",
                path=f"/memories/active_tickets/{calculation_id}.md",
                old_str=f"## {section}\n[empty]",
                new_str=f"## {section}\n{content}"
            )
            return result.get("success") or result.get("error")

        elif tool_name == "send_email":
            result = send_email(**tool_input)
            return str(result)

        else:
            return f"Unknown tool: {tool_name}"

    except Exception as e:
        return f"Tool error: {str(e)}"

def _create_ticket(calculation_id: str, supplier_email: dict) -> None:
    content = textwrap.dedent(f"""
        # Ticket: {calculation_id}
        status: open
        supplier_id: {supplier_email.get('from')}
        loop_count: 0
        created_at: {datetime.now(timezone.utc).isoformat()}

        ## Dispute
        {supplier_email.get('body')}

        ## Analyst Findings
        [empty]

        ## Supervisor Notes
        [empty]

        ## Thread
        [empty]
    """).lstrip()

    memory.execute(
        command="create",
        path=f"/memories/active_tickets/{calculation_id}.md",
        file_text=content
    )

def _write_analyst_findings(calculation_id: str, findings: str) -> None:
    memory.execute(
        command="str_replace",
        path=f"/memories/active_tickets/{calculation_id}.md",
        old_str="## Analyst Findings\n[empty]",   # must match exactly
        new_str=f"## Analyst Findings\n{findings}"
    )



def run_supervisor(email_id: str) -> str:
    """
    Full dispute lifecycle for one email.

    Args:
        email_id: e.g. "dispute_001"

    Returns:
        Final supervisor decision and action taken
    """
    from tools.mail_tools import read_email

    # Step 1 — read the email
    email = read_email(email_id)
    if "error" in email:
        return f"Error reading email: {email['error']}"

    calculation_id = email["calculation_id"]
    print(f"\n📨 Dispute received for: {calculation_id}")

    # Step 2 — create ticket
    _create_ticket(calculation_id, email)
    print(f"📁 Ticket created: {calculation_id}")

    # Step 3 — read knowledge graph
    calc = get_calculation(calculation_id)
    if calc:
        supplier_name = calc[0].get("funded_supplier_name", "")
        category = calc[0].get("category", "")
        kg = _read_knowledge_graph(supplier_name, category)
        week = calc[0].get("year_week_number")
    else:
        supplier_name = ""
        category = ""
        kg = ""
        week = None

    # Step 4 — run analyst
    print(f"\n🔍 Running analyst...")
    analyst_findings = run_analyst(
        calculation_id=calculation_id,
        dispute_context=email["body"],
        supplier_knowledge=kg 
    )
    print(f"\n✅ Analyst complete")

    # Step 4 — write findings to ticket
    _write_analyst_findings(calculation_id, analyst_findings)

    # Step 5 — supervisor decides and acts
    client = get_claude_client()

    messages = [{
        "role": "user",
        "content": f"""
        Dispute: {calculation_id}
        Supplier: {email['from']}
        Subject: {email['subject']}

        Analyst findings:
        {analyst_findings}

        Read the ticket, decide the action, send the appropriate email,
        update the ticket with what you did.
        """
    }]

    response, messages = run_conversation_loop(
        client=client,
        model=MODEL,
        system_prompt=SUPERVISOR_SYSTEM_PROMPT,
        messages=messages,
        tools=SUPERVISOR_TOOLS,
        tool_executor=supervisor_tool_executor,
        max_turns=MAX_AGENT_TURNS,
        max_tokens=2048,
        verbose=True
    )

    _update_knowledge_graph(
    supplier_name=supplier_name,
    category=category,
    calc_id=calculation_id,
    week=calc[0].get("year_week_number"),
    outcome="CORRECT",        # parse from analyst_findings
    summary="Volume dispute — supplier claimed X, confirmed Y",
    agent_notes="Accepts explanation with sales breakdown attached"
    )


    return response.content[0].text




