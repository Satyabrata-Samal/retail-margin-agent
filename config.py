# config.py
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).parent   # always margin-agent/ regardless of run location

load_dotenv(dotenv_path=BASE_DIR / ".env")

# --- LLM ---
MODEL = "claude-haiku-4-5"
MAX_TOKENS = 1024
MAX_AGENT_TURNS = 5

# --- Anthropic client ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# --- Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# --- Memory ---
MEMORY_BASE_PATH = BASE_DIR / "memory_storage"
COMPRESSION_WORD_THRESHOLD = 7500

# --- Email ---
INBOX_DIR = BASE_DIR / "mock_emails"
SENT_DIR = BASE_DIR / "mock_emails" / "sent"

# --- Context management ---
CONTEXT_MANAGEMENT = {
    "edits": [{
        "type": "clear_tool_uses_20250919",
        "trigger": {"type": "input_tokens", "value": 20000},
        "keep": {"type": "tool_uses", "value": 3},
        "clear_at_least": {"type": "input_tokens", "value": 5000}
    }]
}