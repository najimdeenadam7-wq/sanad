"""Parses whatever sources exist into display-ready structures (client-agnostic)."""
import json, re
from pathlib import Path

DL = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(.*)$")

def _read(p): return p.read_text(encoding="utf-8") if p.exists() else ""

def load(client_dir: Path, meta: dict) -> dict:
    cr     = _read(client_dir/"cr_certificate.md")
    crm    = _read(client_dir/"crm_notes.md")
    emails = _read(client_dir/"emails.md")
    news   = _read(client_dir/"news.md")
    reg    = _read(client_dir/"registry.md")
    fin    = json.loads(_read(client_dir/"financials.json") or "{}")
    kyc    = json.loads(_read(client_dir/"kyc_status.json") or "{}")
    req_p  = client_dir.parent/"required_docs.json"
    required = json.loads(req_p.read_text(encoding="utf-8")) if req_p.exists() else []
    up_int = "\n".join(p.read_text(encoding="utf-8") for p in sorted(client_dir.glob("int_up_*.md")))
    up_ext = "\n".join(p.read_text(encoding="utf-8") for p in sorted(client_dir.glob("ext_up_*.md")))
    int_text = crm + "\n" + emails + "\n" + up_int
    ext_text = news + "\n" + up_ext
    combined = "\n".join(t for t in (cr, int_text, ext_text, reg) if t)

    def grab(pattern, default="—"):
        m = re.search(pattern, combined)
        return m.group(1).strip() if m else default

    profile = {"Client": meta.get("name", client_dir.name), "Sector": meta.get("sector", "—")}
    if meta.get("cr"): profile["CR No."] = meta["cr"]
    for key, pat in [("CR No.", r"CR No\.:\s*([^\s|]+)"), ("Activity", r"Activity:\s*([^\n|]+)"),
        ("Registered Capital", r"Registered capital:\s*([^|\n]+)"),
        ("Signatories", r"Signatories:\s*([^\n]+)"), ("Valid Until", r"Valid until:\s*([^\n]+)"),
        ("Registry Status", r"status\s+(\w+)"), ("Relationship Manager", r"RM:\s*(.+)")]:
        v = grab(pat)
        if v != "—": profile[key] = v

    def tag(line):
        if line in crm: return "CRM"
        if line in emails: return "Email"
        return "Upload"
    timeline = []
    for line in int_text.splitlines():
        m = DL.match(line.strip())
        if m: timeline.append((m.group(1), tag(line.strip()), m.group(2)))
    timeline.sort()

    shareholders = []
    m = re.search(r"Shareholders:\s*(.+)", combined)
    if m:
        for part in m.group(1).split(","):
            pm = re.match(r"\s*(.+?)\s+(\d+)%", part)
            if pm: shareholders.append((pm.group(1), f"{pm.group(2)}%"))
    # Only POSITIVE encumbrances warn; "No registered liens…" is a clean signal, not a warning.
    registry_notes = [l.strip() for l in combined.splitlines()
                      if re.search(r"mortgage|lien", l, re.I) and not l.strip().lower().startswith("no ")]

    news_items = [(m.group(1), m.group(2)) for l in ext_text.splitlines() if (m := DL.match(l.strip()))]

    docs = None
    if kyc:
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
    ] if f25 else []
    return dict(profile=profile, timeline=timeline, shareholders=shareholders,
                registry_notes=registry_notes, news=news_items, docs=docs,
                metrics=metrics, fin=fin, kyc=kyc, required=required)
