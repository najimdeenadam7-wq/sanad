"""Parses raw client files into structured, display-ready objects (no more raw JSON dumps)."""
import json, re
from pathlib import Path

DL = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(.*)$")

def load(client_dir: Path, meta: dict) -> dict:
    cr     = (client_dir/"cr_certificate.md").read_text()
    fin    = json.loads((client_dir/"financials.json").read_text())
    kyc    = json.loads((client_dir/"kyc_status.json").read_text())
    crm    = (client_dir/"crm_notes.md").read_text()
    emails = (client_dir/"emails.md").read_text()
    news   = (client_dir/"news.md").read_text()
    reg    = (client_dir/"registry.md").read_text()
    required = json.loads((client_dir.parent/"required_docs.json").read_text())

    def grab(pattern, text, default="—"):
        m = re.search(pattern, text)
        return m.group(1).strip() if m else default

    profile = {
        "Client": meta["name"], "Sector": meta["sector"],
        "CR No.": grab(r"CR No\.:\s*([^\s|]+)", cr),
        "Activity": grab(r"Activity:\s*([^|\n]+)", cr),
        "Registered Capital": grab(r"Registered capital:\s*([^|\n]+)", cr),
        "Signatories": grab(r"Signatories:\s*([^\n]+)", cr),
        "Valid Until": grab(r"Valid until:\s*([^\n]+)", cr),
        "Registry Status": grab(r"status\s+(\w+)", reg),
    }
    timeline = []
    for line in crm.splitlines():
        line = line.strip()
        m = DL.match(line)
        if m: timeline.append((m.group(1), "CRM", m.group(2)))
        rm = re.match(r"RM:\s*(.+)", line)
        if rm: profile["Relationship Manager"] = rm.group(1)
    for line in emails.splitlines():
        m = DL.match(line.strip())
        if m: timeline.append((m.group(1), "Email", m.group(2)))
    timeline.sort()

    shareholders = []
    m = re.search(r"Shareholders:\s*(.+)", reg)
    if m:
        for part in m.group(1).split(","):
            pm = re.match(r"\s*(.+?)\s+(\d+)%", part)
            if pm: shareholders.append((pm.group(1), f"{pm.group(2)}%"))
    # Only POSITIVE encumbrances warn; "No registered liens…" is a clean signal, not a warning.
    registry_notes = [l.strip() for l in reg.splitlines()
                      if re.search(r"mortgage|lien", l, re.I) and not l.strip().lower().startswith("no ")]

    news_items = [(m.group(1), m.group(2)) for l in news.splitlines() if (m := DL.match(l.strip()))]

    present, expired = set(kyc.get("present", [])), set(kyc.get("expired", []))
    docs = [(d, "EXPIRED" if d in expired else ("PRESENT" if d in present else "MISSING")) for d in required]

    f25, f24 = fin.get("fy2025", {}), fin.get("fy2024", {})
    metrics = [
        ("Revenue (KWD)",            f24.get("revenue_kwd"),    f25.get("revenue_kwd")),
        ("Net Income (KWD)",         f24.get("net_income_kwd"), f25.get("net_income_kwd")),
        ("Total Assets (KWD)",       None, f25.get("total_assets_kwd")),
        ("Total Equity (KWD)",       None, f25.get("total_equity_kwd")),
        ("Interest-bearing Debt (KWD)", None, f25.get("interest_bearing_debt_kwd")),
        ("Gross Margin (%)",         None, f25.get("gross_margin_pct")),
        ("Interest Income (%)",      None, f25.get("interest_income_pct")),
    ]
    return dict(profile=profile, timeline=timeline, shareholders=shareholders,
                registry_notes=registry_notes, news=news_items, docs=docs,
                metrics=metrics, fin=fin)