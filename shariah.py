"""Rules-based Shariah pre-screen — the Warba-specific differentiator."""
SCREENED = ["alcohol","gambling","gaming","tobacco","pork","conventional insurance"]

def screen(fin: dict, chunks):
    flags, fy = [], fin.get("fy2025", {})
    fin_chunk = next((c for c in chunks if c.doc == "financials.json"), None)
    ev = fin_chunk.chunk_id if fin_chunk else "n/a"
    ii = fy.get("interest_income_pct", 0.0)
    if ii > 0:
        flags.append(dict(rule="R1 interest income", severity="HIGH",
            finding=f"Conventional interest income of {ii}% of revenue detected (idle cash in conventional deposit).",
            evidence=ev, recommendation="Income-purification plan (charitable disposal) and migrate idle cash to Warba Islamic structures; refer to Shariah Control Unit per AAOIFI Shari'ah standards."))
    assets = fy.get("total_assets_kwd", 1); debt = fy.get("interest_bearing_debt_kwd", 0)
    if assets and debt / assets > 0.33:
        flags.append(dict(rule="R2 conventional leverage", severity="MEDIUM",
            finding=f"Interest-bearing debt is {debt/assets:.0%} of total assets.",
            evidence=ev, recommendation="Propose refinancing of conventional debt via Murabaha / Sukuk programme at renewal."))
    for c in chunks:
        low = c.text.lower()
        hit = next((k for k in SCREENED if k in low), None)
        if hit:
            flags.append(dict(rule="R3 screened activity", severity="HIGH",
                finding=f"Screened activity keyword '{hit}' found in source {c.doc}.",
                evidence=c.chunk_id,
                recommendation="Quantify non-compliant revenue share; propose divestment or ring-fencing via SPV per Shariah Board guidance before facility approval."))
            break
    score = max(0, 100 - sum(40 if f["severity"]=="HIGH" else 15 for f in flags))
    return dict(flags=flags, score=score)

def zakat_estimate(fin: dict) -> dict:
    """Simplified corporate Zakat base (net invested funds proxy), 2.5% rate."""
    fy = fin.get("fy2025", {})
    assets = fy.get("total_assets_kwd", 0) or 0
    equity = fy.get("total_equity_kwd", 0) or 0
    idebt = fy.get("interest_bearing_debt_kwd", 0) or 0
    za = assets * 0.6
    stl = max(0, assets - equity - idebt)
    base = max(0, za - stl)
    return dict(zakatable_assets=za, short_term_liabilities=stl, net_base=base, zakat_due=base * 0.025)