"""Rules-based Shariah pre-screen. Financials optional: without them only R3 (screened
activity keyword scan over all sources) applies."""
import os

SCREENED = ["alcohol","gambling","gaming","tobacco","pork","conventional insurance"]
II_THRESHOLD = float(os.environ.get("SANAD_II_THRESHOLD", "0.0"))
II_MATERIAL = 5.0

def screen(fin: dict, chunks):
    flags, fy = [], (fin or {}).get("fy2025", {})
    fin_chunk = next((c for c in chunks if c.doc == "financials.json"), None)
    ev = fin_chunk.chunk_id if fin_chunk else "n/a"
    ii = fy.get("interest_income_pct", 0.0)
    if fy and ii > II_THRESHOLD:
        high = ii > II_MATERIAL
        flags.append(dict(rule="R1 interest income", severity="HIGH" if high else "MEDIUM",
            finding=f"Conventional interest income of {ii}% of revenue detected (screening threshold {II_THRESHOLD}%).",
            evidence=ev,
            recommendation=("Income-purification plan (charitable disposal) and migrate idle cash to Warba Islamic "
                            "structures; refer to Shariah Control Unit per AAOIFI Shari'ah standards."
                            if high else
                            "Below 5% materiality: purify interest income via charitable disposal per SCU "
                            "methodology, monitor quarterly; propose Wakala placement for idle cash.")))
    assets = fy.get("total_assets_kwd", 0); debt = fy.get("interest_bearing_debt_kwd", 0)
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
    return dict(flags=flags, score=score, threshold=II_THRESHOLD)

def zakat_estimate(fin: dict):
    """Simplified corporate Zakat base (net invested funds proxy), 2.5% rate. None without FY figures."""
    fy = (fin or {}).get("fy2025", {})
    if not fy: return None
    assets = fy.get("total_assets_kwd", 0) or 0
    equity = fy.get("total_equity_kwd", 0) or 0
    idebt = fy.get("interest_bearing_debt_kwd", 0) or 0
    za = assets * 0.6
    stl = max(0, assets - equity - idebt)
    base = max(0, za - stl)
    return dict(zakatable_assets=za, short_term_liabilities=stl, net_base=base, zakat_due=base * 0.025)

def explain_score_diff(previous_score: int, new_score: int, previous_flags: list, new_flags: list) -> dict:
    """Explains why the Shariah/Risk score changed between evaluations."""
    delta = new_score - previous_score
    prev_rules = {f.get("rule") or f.get("rule_id") for f in (previous_flags or [])}
    new_rules = {f.get("rule") or f.get("rule_id") for f in (new_flags or [])}
    
    added_rules = [f for f in new_flags if (f.get("rule") or f.get("rule_id")) not in prev_rules]
    cleared_rules = [f for f in previous_flags if (f.get("rule") or f.get("rule_id")) not in new_rules]
    
    reasons = []
    if delta < 0:
        for f in added_rules:
            rule_name = f.get("rule") or f.get("rule_id")
            reasons.append(f"Score decreased due to new flag: {rule_name} - {f.get('finding', '')}")
    elif delta > 0:
        for f in cleared_rules:
            rule_name = f.get("rule") or f.get("rule_id")
            reasons.append(f"Score improved as issue resolved: {rule_name}")
    else:
        reasons.append("Score unchanged across document revisions.")
        
    return {
        "previous_score": previous_score,
        "new_score": new_score,
        "delta": delta,
        "summary": f"Score changed by {delta:+d} points" if delta != 0 else "Score unchanged (steady)",
        "reasons": reasons,
        "added_flags": added_rules,
        "cleared_flags": cleared_rules
    }

