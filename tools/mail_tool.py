import json
from pathlib import Path
from datetime import datetime, timezone

INBOX_DIR = Path("mock_emails")
SENT_DIR = Path("mock_emails/sent")

SENT_DIR.mkdir(parents=True, exist_ok=True)


def read_email(email_id: str) -> dict:
    """
    Read a mock email from the inbox folder.

    Args:
        email_id: e.g. "dispute_001"

    Returns:
        Email dict with from, subject, body, calculation_id etc.
    """
    path = INBOX_DIR / f"{email_id}.json"

    if not path.exists():
        return {"error": f"Email not found: {email_id}"}

    with open(path, "r") as f:
        return json.load(f)


def send_email(to: str, subject: str, body: str, calculation_id: str) -> dict:
    """
    Mock send an email. Writes to mock_emails/sent/ folder.

    Args:
        to: recipient email address
        subject: email subject
        body: email body
        calculation_id: links email to a dispute ticket

    Returns:
        Status dict
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    filename = f"{calculation_id}_{timestamp}.json"
    path = SENT_DIR / filename

    payload = {
        "to": to,
        "subject": subject,
        "body": body,
        "calculation_id": calculation_id,
        "sent_at": timestamp
    }

    with open(path, "w") as f:
        json.dump(payload, f, indent=2)

    return {
        "status": "sent",
        "to": to,
        "subject": subject,
        "file": str(path)
    }
