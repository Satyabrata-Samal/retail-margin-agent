import streamlit as st
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# ── path setup ────────────────────────────────────────────────
sys.path.append(str(Path(__file__).parent))

from agents.supervisor import run_supervisor
from tools.mail_tools import read_email
from tools.memory_tools import MemoryToolHandler
from config import MEMORY_BASE_PATH

memory = MemoryToolHandler(base_path=MEMORY_BASE_PATH)

# ── page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Margin Discovery Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── styling ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.stApp {
    background-color: #0f1117;
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #161b27;
    border-right: 1px solid #1e2d40;
}

/* Headers */
h1 { 
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.4rem !important;
    color: #38bdf8 !important;
    letter-spacing: -0.02em;
    border-bottom: 1px solid #1e2d40;
    padding-bottom: 0.75rem;
    margin-bottom: 1.5rem !important;
}
h2, h3 {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Cards */
.card {
    background: #161b27;
    border: 1px solid #1e2d40;
    border-radius: 6px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.card-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}
.card-value {
    font-size: 1rem;
    color: #e2e8f0;
    font-weight: 500;
}

/* Status badges */
.badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.05em;
}
.badge-correct   { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.badge-wrong     { background: #431407; color: #fb923c; border: 1px solid #9a3412; }
.badge-pending   { background: #1e1b4b; color: #818cf8; border: 1px solid #3730a3; }
.badge-escalated { background: #2d1b00; color: #fbbf24; border: 1px solid #92400e; }
.badge-open      { background: #0c1a2e; color: #38bdf8; border: 1px solid #0369a1; }

/* Email display */
.email-box {
    background: #0d1117;
    border: 1px solid #1e2d40;
    border-left: 3px solid #38bdf8;
    border-radius: 4px;
    padding: 1rem 1.25rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    color: #94a3b8;
    white-space: pre-wrap;
    line-height: 1.7;
}

/* Ticket display */
.ticket-box {
    background: #0d1117;
    border: 1px solid #1e2d40;
    border-radius: 4px;
    padding: 1rem 1.25rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: #64748b;
    white-space: pre-wrap;
    line-height: 1.8;
    max-height: 400px;
    overflow-y: auto;
}
.ticket-box strong { color: #38bdf8; }

/* Log stream */
.log-line {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    padding: 0.2rem 0;
    border-bottom: 1px solid #1a2233;
    color: #64748b;
}
.log-line.tool  { color: #a78bfa; }
.log-line.turn  { color: #38bdf8; border-bottom: 1px solid #1e2d40; padding-top: 0.5rem; }
.log-line.done  { color: #4ade80; }
.log-line.error { color: #f87171; }

/* Buttons */
.stButton > button {
    background: #0ea5e9 !important;
    color: #0f1117 !important;
    border: none !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    padding: 0.5rem 1.5rem !important;
    border-radius: 4px !important;
}
.stButton > button:hover {
    background: #38bdf8 !important;
}

/* Selectbox, text input */
.stSelectbox > div > div,
.stTextInput > div > div > input {
    background-color: #161b27 !important;
    border: 1px solid #1e2d40 !important;
    color: #e2e8f0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* Metric */
[data-testid="stMetric"] {
    background: #161b27;
    border: 1px solid #1e2d40;
    border-radius: 6px;
    padding: 1rem;
}
[data-testid="stMetricLabel"] { color: #475569 !important; font-size: 0.72rem !important; }
[data-testid="stMetricValue"] { color: #38bdf8 !important; font-family: 'IBM Plex Mono', monospace !important; }

/* Divider */
hr { border-color: #1e2d40 !important; }

/* Expander */
.streamlit-expanderHeader {
    background: #161b27 !important;
    border: 1px solid #1e2d40 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    color: #64748b !important;
}
</style>
""", unsafe_allow_html=True)


# ── helpers ───────────────────────────────────────────────────

def get_mock_emails():
    inbox = Path("mock_emails")
    if not inbox.exists():
        return []
    return [f.stem for f in inbox.glob("*.json") if f.is_file()]


def get_sent_emails():
    sent = Path("mock_emails/sent")
    if not sent.exists():
        return []
    files = sorted(sent.glob("*.json"), reverse=True)
    emails = []
    for f in files:
        with open(f) as fp:
            emails.append(json.load(fp))
    return emails


def get_active_tickets():
    result = memory.execute(command="view", path="/memories/active_tickets")
    if "error" in result:
        return []
    lines = result["success"].split("\n")[1:]  # skip header
    return [l.replace("- ", "").replace(".md", "").strip() for l in lines if l.strip()]


def get_archive_files():
    result = memory.execute(command="view", path="/memories/archive")
    if "error" in result:
        return []
    lines = result["success"].split("\n")[1:]
    return [l.replace("- ", "").strip() for l in lines if l.strip()]


def read_ticket(calculation_id):
    result = memory.execute(
        command="view",
        path=f"/memories/active_tickets/{calculation_id}.md"
    )
    return result.get("success") or result.get("error", "Not found")


def badge(text, kind="open"):
    return f'<span class="badge badge-{kind}">{text}</span>'


def outcome_badge(text):
    text_upper = text.upper() if text else ""
    if "CORRECT" in text_upper:
        return badge("CORRECT", "correct")
    elif "WRONG" in text_upper:
        return badge("WRONG", "wrong")
    elif "CONCLUSIVE" in text_upper:
        return badge("NOT CONCLUSIVE", "escalated")
    elif "SENT" in text_upper:
        return badge("EXPLANATION SENT", "correct")
    elif "AWAITING" in text_upper:
        return badge("AWAITING HUMAN", "wrong")
    elif "ESCALATED" in text_upper:
        return badge("ESCALATED", "escalated")
    return badge("PENDING", "pending")


# ── sidebar ───────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 📊 Margin Discovery")
    st.markdown('<p style="font-family:IBM Plex Mono;font-size:0.7rem;color:#334155;margin-top:-0.5rem">Dispute Automation Agent</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### Navigation")
    page = st.radio(
        "",
        ["📊  Dashboard", "📨  Process Dispute", "📁  Active Tickets", "📤  Sent Emails", "🗄️  Archive"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # quick stats
    tickets = get_active_tickets()
    sent = get_sent_emails()
    st.metric("Active Tickets", len(tickets))
    st.metric("Emails Sent", len(sent))


# ── pages ─────────────────────────────────────────────────────

# ── DASHBOARD ─────────────────────────────────────────────────
if page == "🏠  Dashboard":
    st.markdown("# Margin Discovery Agent")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Tickets", len(get_active_tickets()))
    with col2:
        st.metric("Emails Sent", len(get_sent_emails()))
    with col3:
        archive = get_archive_files()
        st.metric("Archived Suppliers", len(archive))
    with col4:
        inbox = get_mock_emails()
        st.metric("Inbox", len(inbox))

    st.markdown("---")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### Active Tickets")
        tickets = get_active_tickets()
        if not tickets:
            st.markdown('<div class="card"><span style="color:#334155;font-family:IBM Plex Mono;font-size:0.8rem">No active tickets</span></div>', unsafe_allow_html=True)
        for t in tickets:
            content = read_ticket(t)
            status = "open"
            for line in content.split("\n"):
                if line.startswith("status:"):
                    status = line.replace("status:", "").strip()
            st.markdown(f'''
            <div class="card">
                <div class="card-header">Calculation ID</div>
                <div class="card-value">{t} &nbsp; {outcome_badge(status)}</div>
            </div>
            ''', unsafe_allow_html=True)

    with col_right:
        st.markdown("### Recent Sent Emails")
        sent = get_sent_emails()[:5]
        if not sent:
            st.markdown('<div class="card"><span style="color:#334155;font-family:IBM Plex Mono;font-size:0.8rem">No sent emails</span></div>', unsafe_allow_html=True)
        for email in sent:
            st.markdown(f'''
            <div class="card">
                <div class="card-header">{email.get("sent_at", "")}</div>
                <div class="card-value" style="font-size:0.88rem">{email.get("subject", "")}</div>
                <div style="font-size:0.78rem;color:#475569;margin-top:0.25rem;font-family:IBM Plex Mono">→ {email.get("to", "")}</div>
            </div>
            ''', unsafe_allow_html=True)


# ── PROCESS DISPUTE ───────────────────────────────────────────
elif page == "📨  Process Dispute":
    st.markdown("# Process Dispute")

    inbox_emails = get_mock_emails()

    if not inbox_emails:
        st.warning("No emails found in mock_emails/ folder.")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_email = st.selectbox(
                "Select email to process",
                inbox_emails,
                format_func=lambda x: f"📧  {x}"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            run_btn = st.button("▶  Run Agent")

        # Preview selected email
        if selected_email:
            email_data = read_email(selected_email)
            if "error" not in email_data:
                st.markdown("### Email Preview")
                st.markdown(f'''
                <div class="email-box">From:    {email_data.get("from", "")}
Subject: {email_data.get("subject", "")}
Date:    {email_data.get("received_at", "")}
CalcID:  {email_data.get("calculation_id", "")}

{email_data.get("body", "")}
                </div>
                ''', unsafe_allow_html=True)

        # Run agent
        if run_btn and selected_email:
            st.markdown("### Agent Log")
            log_container = st.container()

            with st.spinner("Agent running..."):
                log_lines = []

                # Capture stdout by running with streaming output
                with log_container:
                    progress = st.empty()
                    progress.markdown('<div class="log-line turn">🚀 Starting agent pipeline...</div>', unsafe_allow_html=True)

                try:
                    result = run_supervisor(selected_email)

                    # Show result
                    st.markdown("---")
                    st.markdown("### Result")
                    st.markdown(f'''
                    <div class="card">
                        <div class="card-header">Agent Decision</div>
                        <div class="card-value" style="font-size:0.9rem;line-height:1.6;white-space:pre-wrap">{result}</div>
                    </div>
                    ''', unsafe_allow_html=True)

                    # Show updated ticket
                    calc_id = read_email(selected_email).get("calculation_id")
                    if calc_id:
                        st.markdown("### Updated Ticket")
                        ticket_content = read_ticket(calc_id)
                        st.markdown(f'<div class="ticket-box">{ticket_content}</div>', unsafe_allow_html=True)

                    st.success("✅ Dispute processed successfully")

                except Exception as e:
                    st.error(f"Agent error: {str(e)}")


# ── ACTIVE TICKETS ────────────────────────────────────────────
elif page == "📁  Active Tickets":
    st.markdown("# Active Tickets")

    tickets = get_active_tickets()

    if not tickets:
        st.markdown('<div class="card"><span style="color:#334155;font-family:IBM Plex Mono;font-size:0.8rem">No active tickets found</span></div>', unsafe_allow_html=True)
    else:
        selected = st.selectbox(
            "Select ticket",
            tickets,
            format_func=lambda x: f"🎫  {x}"
        )

        if selected:
            content = read_ticket(selected)

            # Parse sections
            sections = {}
            current_section = "header"
            current_lines = []

            for line in content.split("\n"):
                if line.startswith("## "):
                    sections[current_section] = "\n".join(current_lines).strip()
                    current_section = line.replace("## ", "").strip()
                    current_lines = []
                else:
                    current_lines.append(line)
            sections[current_section] = "\n".join(current_lines).strip()

            # Header info
            header = sections.get("header", "")
            col1, col2, col3 = st.columns(3)
            for line in header.split("\n"):
                if "status:" in line:
                    status_val = line.split(":", 1)[1].strip()
                    with col1:
                        st.markdown(f'''<div class="card">
                            <div class="card-header">Status</div>
                            <div class="card-value">{outcome_badge(status_val)}</div>
                        </div>''', unsafe_allow_html=True)
                elif "supplier_id:" in line:
                    with col2:
                        st.markdown(f'''<div class="card">
                            <div class="card-header">Supplier</div>
                            <div class="card-value" style="font-size:0.82rem">{line.split(":",1)[1].strip()}</div>
                        </div>''', unsafe_allow_html=True)
                elif "loop_count:" in line:
                    with col3:
                        st.markdown(f'''<div class="card">
                            <div class="card-header">Loop Count</div>
                            <div class="card-value">{line.split(":",1)[1].strip()}</div>
                        </div>''', unsafe_allow_html=True)

            # Sections
            for section_name in ["Dispute", "Analyst Findings", "Supervisor Notes", "Thread"]:
                content_val = sections.get(section_name, "[empty]")
                with st.expander(f"📄  {section_name}", expanded=(section_name == "Analyst Findings")):
                    st.markdown(f'<div class="ticket-box">{content_val}</div>', unsafe_allow_html=True)


# ── SENT EMAILS ───────────────────────────────────────────────
elif page == "📤  Sent Emails":
    st.markdown("# Sent Emails")

    sent = get_sent_emails()

    if not sent:
        st.markdown('<div class="card"><span style="color:#334155;font-family:IBM Plex Mono;font-size:0.8rem">No sent emails</span></div>', unsafe_allow_html=True)
    else:
        for email in sent:
            with st.expander(f"📧  {email.get('subject', 'No subject')}  —  {email.get('sent_at', '')}"):
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown(f'''<div class="card">
                        <div class="card-header">To</div>
                        <div class="card-value" style="font-size:0.85rem">{email.get("to", "")}</div>
                    </div>''', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'''<div class="card">
                        <div class="card-header">Calculation ID</div>
                        <div class="card-value">{email.get("calculation_id", "")}</div>
                    </div>''', unsafe_allow_html=True)

                st.markdown(f'<div class="email-box">{email.get("body", "")}</div>', unsafe_allow_html=True)


# ── ARCHIVE ───────────────────────────────────────────────────
elif page == "🗄️  Archive":
    st.markdown("# Supplier Archive")
    st.markdown('<p style="font-family:IBM Plex Mono;font-size:0.78rem;color:#475569;margin-top:-1rem">Closed ticket summaries by supplier-category</p>', unsafe_allow_html=True)

    archive_files = get_archive_files()

    if not archive_files:
        st.markdown('<div class="card"><span style="color:#334155;font-family:IBM Plex Mono;font-size:0.8rem">No archived tickets yet. Archives are created when tickets close.</span></div>', unsafe_allow_html=True)
    else:
        for fname in archive_files:
            result = memory.execute(
                command="view",
                path=f"/memories/archive/{fname}"
            )
            content = result.get("success", "")
            supplier_name = fname.replace(".md", "").replace("-", " · ")

            with st.expander(f"🗂️  {supplier_name}"):
                st.markdown(f'<div class="ticket-box">{content}</div>', unsafe_allow_html=True)