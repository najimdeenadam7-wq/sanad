"""KYC gap detection: exact (kyc_status.json) or heuristic keyword scan of uploaded chunks."""
import json
from pathlib import Path

KEYWORDS = {
    "Commercial Registration Certificate": ["commercial registration", "cr no."],
    "Signatory Passport Copies": ["passport"],
    "Board Resolution - Credit Facility": ["board resolution", "it was resolved"],
    "Audited Financials FY2024": ["fy2024"],
    "Audited Financials FY2025": ["audited", "fy2025", "auditor's report"],
    "AML/KYC Screening Report (valid)": ["aml", "screening report", "kyc"],
    "Ultimate Beneficial Ownership Declaration": ["beneficial ownership", "ubo"],
    "Insurance Coverage Summary": ["insurance coverage", "policy"],
}

def detect(kyc, client_name, chunks=None, required_path=Path("data/required_docs.json")):
    required = json.loads(required_path.read_text(encoding="utf-8")) if required_path.exists() else list(KEYWORDS)
    items = []
    if kyc:
        present, expired = set(kyc.get("present", [])), set(kyc.get("expired", []))
        for doc in required:
            if doc in expired: items.append(dict(doc=doc, status="EXPIRED"))
            elif doc not in present: items.append(dict(doc=doc, status="MISSING"))
    else:
        text = " ".join(c.text.lower() for c in (chunks or []))
        for doc in required:
            hit = any(k in text for k in KEYWORDS.get(doc, [doc.lower()]))
            items.append(dict(doc=doc, status="DETECTED" if hit else "MISSING"))
    outstanding = [i for i in items if i["status"] in ("MISSING", "EXPIRED")]
    lines = "\n".join(f"  {n}. {i['doc']} ({i['status'].title()})" for n, i in enumerate(outstanding, 1))
    email = f"""Subject: Outstanding documentation - {client_name}

Dear Client Finance Team,
To progress your credit facility review with Warba Bank, kindly provide:
{lines if lines else '  (none - file complete)'}
These items are required under CBK KYC standards and our credit policy.
Regards, Relationship Management - Warba Bank Corporate Banking"""
    return dict(items=items, email=email, hours_saved=0.75*len(outstanding))
