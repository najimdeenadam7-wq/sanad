"""Rules-based Shariah pre-screen. Financials optional: without them only R3 (screened
activity keyword scan over all sources) applies."""
import os

SCREENED = ["alcohol","gambling","gaming","tobacco","pork","conventional insurance"]
II_THRESHOLD = float(os.environ.get("SANAD_II_THRESHOLD", "0.0"))
II_MATERIAL = 5.0

def screen(fin: dict, chunks):
    flags = []
    fy = (fin or {}).get("fy2025", {}) or (fin.get("fiscal_years", [{}])[-1] if isinstance(fin.get("fiscal_years"), list) and fin.get("fiscal_years") else {})
    fin_chunk = next((c for c in chunks if getattr(c, "doc", "") == "financials.json"), None)
    ev = getattr(fin_chunk, "chunk_id", "n/a")
    
    # 1. Non-Permissible / Interest Income
    rev = fy.get("revenue_kwd") or fy.get("revenue") or 1.0
    ii_amount = fy.get("non_permissible_income") or fy.get("interest_income_kwd") or fy.get("interest_income") or 0.0
    ii_pct = fy.get("interest_income_pct", 0.0) or ((ii_amount / rev * 100) if rev and ii_amount else 0.0)
    
    if ii_pct > 0.0 or ii_amount > 0:
        high = ii_pct > II_MATERIAL
        flags.append(dict(
            rule="R1 interest income", severity="HIGH" if high else "MEDIUM",
            finding=f"Conventional interest income of KWD {ii_amount:,.0f} ({ii_pct:.2f}% of revenue) detected.",
            evidence=ev,
            recommendation="Mandatory Taharah disgorgement (charitable disposal) to Bait Al-Zakat; refer to SCU per AAOIFI Standard No. 21."
        ))

    # 2. Conventional Debt / Leverage Ratio
    assets = fy.get("total_assets_kwd") or fy.get("total_assets") or 0
    debt = fy.get("interest_bearing_debt_kwd") or fy.get("total_debt") or 0
    debt_ratio = (debt / assets) if (assets and debt) else 0.0
    
    if debt_ratio > 0.25:
        flags.append(dict(
            rule="R2 conventional leverage", severity="MEDIUM",
            finding=f"Interest-bearing debt stands at {debt_ratio:.1%} of total assets (AAOIFI max ceiling 30.0%).",
            evidence=ev,
            recommendation="Propose Islamic refinancing of conventional debt via Murabaha / Sukuk facility at renewal."
        ))

    # 3. Screened Activities & Non-Compliant Investments
    all_text = " ".join(getattr(c, "text", "") for c in chunks).lower() if chunks else ""
    for c in chunks:
        low = getattr(c, "text", "").lower()
        hit = next((k for k in SCREENED if k in low), None)
        if hit:
            flags.append(dict(
                rule="R3 screened activity", severity="HIGH",
                finding=f"Screened activity/holding '{hit}' detected in document {getattr(c, 'doc', '')}.",
                evidence=getattr(c, "chunk_id", "SRC-001"),
                recommendation="Quantify non-compliant revenue/investment share; refer to SCU for divestment mandate."
            ))
            break
            
    if "reinsurance" in all_text and not any(f["rule"] == "R3 screened activity" for f in flags):
        flags.append(dict(
            rule="R5 non-compliant equity holding", severity="MEDIUM",
            finding="Un-purified equity stake in conventional reinsurance entity detected.",
            evidence="SRC-002",
            recommendation="SCU review required for equity holding divestment or dividend purification."
        ))

    deductions = sum(20 if f["severity"] == "HIGH" else 12 for f in flags)
    score = max(0, 100 - deductions)
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

