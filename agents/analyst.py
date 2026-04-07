ANALYST_SYSTEM_PROMPT = """
You are an analyst agent for Tesco's Margin Discovery team.

Your job is to analyse supplier invoice disputes using data from the database.

You have access to these tools:
- get_calculation: fetch the full calculation row for a dispute
- get_supplier: fetch supplier details including parent/subsidiary info
- get_sales_breakdown: fetch actual weekly sales data for a product
- get_agreement: fetch the agreed funding rate for a promotion
- execute_analyst_query: run a custom SQL query for deeper analysis

## How to approach a dispute

1. Always start by calling get_calculation to get the full invoice row
2. Read the check columns — they tell you where to look first
3. Call get_supplier to understand parent/subsidiary relationship
4. Query sales and agreement data to verify the calculation
5. Form a clear conclusion — one of three outcomes:
   - CORRECT: calculation is right, supplier is wrong
   - WRONG: calculation has an error, needs DB fix
   - NOT_CONCLUSIVE: cannot determine from available data

## Rules
- Only use SELECT queries in execute_analyst_query
- Always state which data you used to reach your conclusion
- Always include the exact numbers — volume, rate, total
- Be precise. The supervisor agent will act on your output.

## DB Schema Reference
suppliers: supplier_number, supplier_name, parent_supplier_number, 
           parent_supplier_name, supplier_type
products: tpnb, tpnb_description, category
promotions: promotion_reference_number, promotion_status, 
            offer_start_date, offer_end_date
agreements: promotion_reference_number, funded_supplier_number, 
            tpnb, supplier_promotion_funding_per_unit,
            funding_start_date, funding_end_date
sales: year_week_number, tpnb, sales_supplier, sup_sales_volume,
       sup_sales_value_xvat
calculations: calculation_id, funded_supplier_number, promo_sales_volume,
              total_supplier_promotion_funding_ex_vat,
              main_subsidiary_alternate, deal_status, final_check

## When to return NOT_CONCLUSIVE

Even if the DB data looks correct, return NOT_CONCLUSIVE when:

1. Supplier claims a COMMERCIAL dispute — cancellation, contract terms, 
   verbal agreements, or anything requiring original contract documents
   to verify. The DB cannot prove a cancellation happened outside the 
   system.

2. Supplier disputes the EXISTENCE of an agreement — "we never agreed 
   to this". Even if an agreement row exists in DB, only the MD team 
   can verify the original signed contract.

3. Data conflict cannot be resolved by SQL alone — conflicting signals 
   across tables with no clear winner.

## Key distinction

DATA dispute  → agent can resolve (volume, rate, dates, maths)
COMMERCIAL dispute → agent cannot resolve → NOT_CONCLUSIVE → escalate

Supplier saying "promotion was cancelled" is a COMMERCIAL dispute.
DB showing approved does not override a commercial cancellation claim.
The MD team needs to verify with the commercial team and contract docs.
"""

ANALYST_TOOLS = [
    {
        "name": "get_calculation",
        "description": "Fetch the full calculation row for a dispute. Always call this first.",
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
        "name": "get_supplier",
        "description": "Fetch supplier details including parent/subsidiary relationship.",
        "input_schema": {
            "type": "object",
            "properties": {
                "supplier_id": {
                    "type": "integer",
                    "description": "Supplier number e.g. 60198"
                }
            },
            "required": ["supplier_id"]
        }
    },
    {
        "name": "get_sales_breakdown",
        "description": "Fetch actual sales data for a product-supplier-week combination.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tpnb": {
                    "type": "integer",
                    "description": "Product number"
                },
                "supplier_id": {
                    "type": "integer",
                    "description": "Supplier number"
                },
                "week": {
                    "type": "integer",
                    "description": "Week number e.g. 202603"
                }
            },
            "required": ["tpnb", "supplier_id", "week"]
        }
    },
    {
        "name": "get_agreement",
        "description": "Fetch the agreed funding rate for a promotion and supplier.",
        "input_schema": {
            "type": "object",
            "properties": {
                "promo_ref": {
                    "type": "integer",
                    "description": "Promotion reference number"
                },
                "supplier_id": {
                    "type": "integer",
                    "description": "Supplier number"
                },
                "tpnb": {
                    "type": "integer",
                    "description": "Product number"
                }
            },
            "required": ["promo_ref", "supplier_id", "tpnb"]
        }
    },
    {
        "name": "execute_analyst_query",
        "description": "Run a custom read-only SQL query for deeper analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "A SELECT query only. No INSERT, UPDATE, DELETE."
                }
            },
            "required": ["sql"]
        }
    }
]

from tools.db_tools import (
    get_calculation,
    get_supplier,
    get_sales_breakdown,
    get_agreement,
    execute_analyst_query
)
from utils.conversation import run_conversation_loop
from clients.claude_client import get_claude_client
from config import MODEL, MAX_TOKENS, MAX_AGENT_TURNS

def analyst_tool_executor(tool_name: str, tool_input: dict) -> str:
    try:
        if tool_name == "get_calculation":
            return str(get_calculation(**tool_input))
        elif tool_name == "get_supplier":
            return str(get_supplier(**tool_input))
        elif tool_name == "get_sales_breakdown":
            return str(get_sales_breakdown(**tool_input))
        elif tool_name == "get_agreement":
            return str(get_agreement(**tool_input))
        elif tool_name == "execute_analyst_query":
            return str(execute_analyst_query(**tool_input))
        else:
            return f"Unknown tool: {tool_name}"
    except Exception as e:
        return f"Tool error: {str(e)}"

def run_analyst(calculation_id: str, dispute_context: str, supplier_knowledge: str) -> str:
    """
    Analyse a dispute and return structured findings. Refer supplier_knowledge, which is the doc of previous resolutions of supplier-category level.

    Args:
        calculation_id: e.g. "YCCP-41"
        dispute_context: supplier email body + any context

    Returns:
        Analysis string — CORRECT / WRONG / NOT_CONCLUSIVE + reasoning
    """
    client = get_claude_client()

    messages = [{
        "role": "user",
        "content": f"""
        Dispute received for calculation: {calculation_id}

        Supplier message:
        {dispute_context}

        For reference previous dispute & resolution doc with patterns:{supplier_knowledge}

        Please analyse this dispute and return:
        1. OUTCOME: CORRECT / WRONG / NOT_CONCLUSIVE
        2. EVIDENCE: exact numbers from DB
        3. REASONING: why you reached this conclusion
        """
    }]

    response, messages = run_conversation_loop(
        client=client,
        model=MODEL,
        system_prompt=ANALYST_SYSTEM_PROMPT,
        messages=messages,
        tools=ANALYST_TOOLS,
        tool_executor=analyst_tool_executor,
        max_turns=MAX_AGENT_TURNS,
        max_tokens=MAX_TOKENS,
        verbose=True
    )

    return response.content[0].text
