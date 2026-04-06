from datetime import datetime, timezone
from tools.memory_tools import MemoryToolHandler
from config import MEMORY_BASE_PATH
from clients.claude_client import get_claude_client
from config import MODEL
import re

memory = MemoryToolHandler(base_path=MEMORY_BASE_PATH)


def _get_kg_path(supplier_name: str, category: str) -> str:
    """Normalise supplier+category into a safe file path."""
    safe_supplier = supplier_name.replace(" ", "-").replace("/", "-")
    safe_category = category.replace(" ", "-").replace("/", "-")
    return f"/memories/archive/{safe_supplier}-{safe_category}.md"


def _read_knowledge_graph(supplier_name: str, category: str) -> str:
    """
    Read the knowledge graph for a supplier-category pair.
    Returns empty template string if file doesn't exist yet.
    """
    path = _get_kg_path(supplier_name, category)
    result = memory.execute(command="view", path=path)

    if "error" in result:
        # File doesn't exist yet — return blank template
        return _empty_template(supplier_name, category)

    return result.get("success", "")

def _update_patterns_with_llm(
    supplier_name: str,
    category: str,
    current_kg: str,
    new_dispute: dict
) -> str:
    """
    Ask Claude to analyse the full dispute history and update
    the Dispute Patterns and Agent Notes sections.

    Returns updated knowledge graph content.
    """

    client = get_claude_client()

    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""You are maintaining a supplier knowledge graph for 
Tesco's Margin Discovery team.

Here is the current knowledge graph:
{current_kg}

A new dispute has just been resolved:
- Calc ID: {new_dispute['calc_id']}
- Week: {new_dispute['week']}
- Outcome: {new_dispute['outcome']}
- Summary: {new_dispute['summary']}

Based on ALL resolved disputes in the history:

1. Update the ## Dispute Patterns section — identify any patterns 
   you see across disputes (volume discrepancies, frequency, 
   promotion types disputed, resolution patterns)

2. Update the ## Agent Notes section — add strategic advice for 
   future disputes with this supplier based on what has worked

Return ONLY the updated ## Dispute Patterns section and 
## Agent Notes section in this exact format:

## Dispute Patterns
- pattern 1
- pattern 2

## Agent Notes  
- note 1
- note 2
"""
        }]
    )

    return response.content[0].text



def _update_knowledge_graph(
    supplier_name: str,
    category: str,
    calc_id: str,
    week: int,
    outcome: str,
    summary: str,
    agent_notes: str = "",
    known_issues: str = ""
) -> None:
    """
    Update the knowledge graph after a dispute closes.

    If file doesn't exist — creates it with first entry.
    If file exists — increments counters, appends dispute row,
    updates patterns and notes.
    """
    path = _get_kg_path(supplier_name, category)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    existing = memory.execute(command="view", path=path)


    # ── CREATE — first dispute for this supplier-category ─────
    if "error" in existing:
        content = _empty_template(supplier_name, category)
        content = _set_counter(content, "total_disputes", 1)
        content = _set_counter(content, "open_disputes", 0)
        content = content.replace(
            "last_updated: ",
            f"last_updated: {timestamp}"
        )
        content = content.replace(
            "| Calc ID | Week | Outcome | Summary |\n|---|---|---|---|\n",
            f"| Calc ID | Week | Outcome | Summary |\n|---|---|---|---|\n"
            f"| {calc_id} | {week} | {outcome} | {summary} |\n"
        )
        if agent_notes:
            content = content.replace(
                "- [populated by agent — strategy hints for future disputes]",
                f"- {agent_notes}"
            )
        if known_issues:
            content = content.replace(
                "- [populated by agent when it spots anomalies]",
                f"- {known_issues}"
            )

        memory.execute(command="create", path=path, file_text=content)
        return

    # ── UPDATE — file exists, increment and append ─────────────
    content = existing["success"]

    # Strip line numbers added by view command (e.g. "   1: ")
    lines = content.split("\n")
    clean_lines = []
    for line in lines:
        if len(line) > 5 and line[:5].strip().isdigit() and line[5] == ":":
            clean_lines.append(line[7:])  # strip "   N: " prefix
        else:
            clean_lines.append(line)
    content = "\n".join(clean_lines)

    content = re.sub(
        r"last_updated:.*",
        f"last_updated: {timestamp}",
        content
    )

    # Increment total_disputes
    match = re.search(r"total_disputes:\s*(\d+)", content)
    if match:
        current = int(match.group(1))
        content = re.sub(
            r"total_disputes:\s*\d+",
            f"total_disputes: {current + 1}",
            content
        )

    # Append to Resolved Disputes table
    new_row = f"| {calc_id} | {week} | {outcome} | {summary} |"
    content = content.replace(
        "|---|---|---|---|",
        f"|---|---|---|---|\n{new_row}",
        1
    )
    new_dispute = {
    "calc_id": calc_id,
    "week": week,
    "outcome": outcome,
    "summary": summary
    }
    if (current + 1) >= 2:   # only after second dispute
        updated_sections = _update_patterns_with_llm(
            supplier_name, category, content, new_dispute
        )

    # Replace Dispute Patterns section
    if "## Dispute Patterns" in updated_sections:
        patterns_match = re.search(
            r"## Dispute Patterns\n(.*?)(?=\n## |\Z)",
            updated_sections,
            re.DOTALL
        )
        if patterns_match:
            new_patterns = patterns_match.group(0)
            content = re.sub(
                r"## Dispute Patterns\n.*?(?=\n## )",
                new_patterns + "\n",
                content,
                flags=re.DOTALL
            )

    # Replace Agent Notes section
    if "## Agent Notes" in updated_sections:
        notes_match = re.search(
            r"## Agent Notes\n(.*?)(?=\n## |\Z)",
            updated_sections,
            re.DOTALL
        )
        if notes_match:
            new_notes = notes_match.group(0)
            content = re.sub(
                r"## Agent Notes\n.*?$",
                new_notes,
                content,
                flags=re.DOTALL | re.MULTILINE
            )
    # Rewrite file
    memory.execute(command="create", path=path, file_text=content)


def _empty_template(supplier_name: str, category: str) -> str:
    """Return a blank knowledge graph template."""
    return (
        f"# Supplier Knowledge: {supplier_name} · {category}\n"
        f"\n"
        f"last_updated: \n"
        f"total_disputes: 0\n"
        f"open_disputes: 0\n"
        f"\n"
        f"## Supplier Profile\n"
        f"parent_name: \n"
        f"parent_id: \n"
        f"subsidiary_name: \n"
        f"subsidiary_id: \n"
        f"contact_email: \n"
        f"currency: GBP\n"
        f"invoicing_entity: \n"
        f"\n"
        f"## Dispute Patterns\n"
        f"- [populated after first resolved dispute]\n"
        f"\n"
        f"## Resolved Disputes\n"
        f"| Calc ID | Week | Outcome | Summary |\n"
        f"|---|---|---|---|\n"
        f"\n"
        f"## Known Issues\n"
        f"- [populated by agent when it spots anomalies]\n"
        f"\n"
        f"## Agent Notes\n"
        f"- [populated by agent — strategy hints for future disputes]\n"
    )


def _set_counter(content: str, field: str, value: int) -> str:
    """Set a numeric counter field in the knowledge graph."""
    import re
    return re.sub(rf"{field}:\s*\d*", f"{field}: {value}", content)