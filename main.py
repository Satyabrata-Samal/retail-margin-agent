import sys
from agents.supervisor import run_supervisor

if __name__ == "__main__":
    email_id = sys.argv[1] if len(sys.argv) > 1 else "dispute_001"
    print(f"\n🚀 Processing: {email_id}")
    result = run_supervisor(email_id)
    print(result)