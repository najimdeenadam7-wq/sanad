"""KYC/document gap detection + auto-drafted client outreach email."""
import json
from pathlib import Path

def detect(kyc: dict, client_name: str, required_path=Path("data/required_docs.json")):
    required = json.loads(required_path.read_text())
    present, expired = set(kyc.get("present", [])), set(kyc.get("expired", []))
    items = []
    for doc in required:
        if doc in expired: items.append(dict(doc=doc, status="EXPIRED"))
        elif doc not in present: items.append(dict(doc=doc, status="MISSING"))
    lines = "\n".join(f"  {i+1}. {it['doc']} ({it['status'].title()})" for i, it in enumerate(items))
    email = f"""Subject: Outstanding documentation - {client_name}

Dear Client Finance Team,
To progress your credit facility review with Warba Bank, kindly provide:
{lines if lines else '  (none - file complete)'}
These items are required under CBK KYC standards and our credit policy.
Regards, Relationship Management - Warba Bank Corporate Banking"""
    return dict(items=items, email=email, hours_saved=0.75*len(items))