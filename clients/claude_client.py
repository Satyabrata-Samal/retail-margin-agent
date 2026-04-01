
import anthropic
from config import ANTHROPIC_API_KEY

def get_claude_client() -> anthropic.Anthropic:
    if not ANTHROPIC_API_KEY:
        raise ValueError("Missing ANTHROPIC_API_KEY in .env")
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)