"""Sanad Financial Calculation & Stress-Testing Engine.
Deterministic, pure mathematical calculations (never guessed by LLM).
Covers DSCR baseline, 3 covenant stress tests, Zakat base, and AAOIFI Shariah purification.
"""
from typing import Dict, Any, List

FORMULA_VERSION = "2026.1"

def calculate_financial_metrics(
    extracted_fin: Dict[str, Any],
    facility_requested: float = 0.0,
    collateral_value: float = 0.0
) -> Dict[str, Any]:
    """Computes comprehensive corporate credit metrics and scenario stress tests."""
    fy_list = extracted_fin.get("fiscal_years", [])
    if fy_list and isinstance(fy_list, list):
        latest_fy = sorted(fy_list, key=lambda x: x.get("year", 0), reverse=True)[0]
    elif isinstance(extracted_fin.get("fy2025"), dict):
        latest_fy = extracted_fin["fy2025"]
    else:
        latest_fy = extracted_fin

    revenue = float(latest_fy.get("revenue") or latest_fy.get("revenue_kwd") or 0.0)
    net_income = float(latest_fy.get("net_income") or latest_fy.get("net_income_kwd") or 0.0)
    total_assets = float(latest_fy.get("total_assets") or latest_fy.get("total_assets_kwd") or 0.0)
    total_equity = float(latest_fy.get("total_equity") or latest_fy.get("total_equity_kwd") or 0.0)
    total_debt = float(latest_fy.get("total_debt") or latest_fy.get("interest_bearing_debt_kwd") or latest_fy.get("interest_bearing_debt") or 0.0)
    interest_income_pct = float(latest_fy.get("interest_income_pct") or 0.0)
    interest_income_kwd = float(latest_fy.get("interest_income_kwd") or (revenue * interest_income_pct / 100.0 if interest_income_pct else 0.0))
    gross_margin_pct = float(latest_fy.get("gross_margin_pct") or 0.0)

    ebitda = float(latest_fy.get("ebitda") or 0.0)
    if ebitda <= 0.0 and revenue > 0.0:
        ebitda = max(net_income * 1.35, revenue * 0.10)

    debt_service = float(latest_fy.get("debt_service") or 0.0)
    if debt_service <= 0.0 and total_debt > 0.0:
        debt_service = total_debt * 0.22
    elif debt_service <= 0.0 and facility_requested > 0.0:
        debt_service = facility_requested * 0.22
    else:
        debt_service = max(debt_service, 1.0)

    net_margin_pct = (net_income / revenue * 100.0) if revenue > 0.0 else 0.0
    debt_to_equity = (total_debt / total_equity) if total_equity > 0.0 else 0.0
    debt_to_assets = (total_debt / total_assets) if total_assets > 0.0 else 0.0
    ltv_ratio = (facility_requested / collateral_value) if collateral_value > 0.0 else 0.0
    dscr_baseline = (ebitda / debt_service) if debt_service > 0.0 else 0.0

    COVENANT_MIN_DSCR = 1.25

    ebitda_shock_rev_15pct = max(0.0, ebitda * (1.0 - 0.15 * 1.8))
    dscr_stress_rev_15pct = ebitda_shock_rev_15pct / debt_service if debt_service > 0.0 else 0.0

    debt_service_shock_rate_150bps = debt_service + (total_debt * 0.015)
    dscr_stress_rate_150bps = ebitda / debt_service_shock_rate_150bps if debt_service_shock_rate_150bps > 0.0 else 0.0

    ebitda_shock_combined = max(0.0, ebitda * (1.0 - 0.10 * 1.8))
    debt_service_combined = debt_service + (total_debt * 0.010)
    dscr_stress_combined = ebitda_shock_combined / debt_service_combined if debt_service_combined > 0.0 else 0.0

    covenant_breached = (
        dscr_stress_rev_15pct < COVENANT_MIN_DSCR or
        dscr_stress_rate_150bps < COVENANT_MIN_DSCR or
        dscr_stress_combined < COVENANT_MIN_DSCR
    )

    covenant_mitigations = []
    if covenant_breached:
        dsra_required_kwd = debt_service * 0.25
        covenant_mitigations.append(
            f'Establish mandatory Debt Service Reserve Account (DSRA) of KWD {dsra_required_kwd:,.0f} (3 months of debt service) prior to first facility drawdown.'
        )
        covenant_mitigations.append(
            'Require quarterly financial covenant compliance certificate with minimum DSCR test maintained at >= 1.25x.'
        )
        if dscr_stress_rate_150bps < COVENANT_MIN_DSCR:
            covenant_mitigations.append(
                "Mandate profit-rate cap or fixed-rate Islamic hedging mechanism (Islamic Profit Rate Swap / Wa'ad) for at least 50% of outstanding facility."
            )
    else:
        covenant_mitigations.append('Standard covenant package: annual audited financial statements within 90 days of fiscal year end; no negative pledge on core operating assets.')

    zakatable_assets = total_assets * 0.60
    short_term_liabilities = max(0.0, total_assets - total_equity - total_debt)
    net_zakat_base = max(0.0, zakatable_assets - short_term_liabilities)
    zakat_due_kwd = net_zakat_base * 0.025

    purification_required = (interest_income_kwd > 0.0 or interest_income_pct > 0.0)
    purification_amount_kwd = max(0.0, interest_income_kwd)

    return {
        "formula_version": FORMULA_VERSION,
        "figures": {
            "revenue_kwd": revenue,
            "net_income_kwd": net_income,
            "total_assets_kwd": total_assets,
            "total_equity_kwd": total_equity,
            "total_debt_kwd": total_debt,
            "ebitda_kwd": round(ebitda, 2),
            "debt_service_kwd": round(debt_service, 2),
            "interest_income_kwd": round(interest_income_kwd, 2)
        },
        "ratios": {
            "net_margin_pct": round(net_margin_pct, 2),
            "gross_margin_pct": round(gross_margin_pct, 2),
            "debt_to_equity": round(debt_to_equity, 2),
            "debt_to_assets": round(debt_to_assets, 2),
            "ltv_ratio": round(ltv_ratio, 2)
        },
        "covenants": {
            "dscr_baseline": round(dscr_baseline, 2),
            "covenant_target": COVENANT_MIN_DSCR,
            "status": "PASS" if dscr_baseline >= COVENANT_MIN_DSCR else "FAIL",
            "stress_scenarios": {
                "revenue_shock_down_15pct": {
                    "shock": "Revenue drops 15%",
                    "stressed_dscr": round(dscr_stress_rev_15pct, 2),
                    "breaches_covenant": dscr_stress_rev_15pct < COVENANT_MIN_DSCR
                },
                "profit_rate_hike_150bps": {
                    "shock": "Benchmark rate increases +150 bps (+1.5%)",
                    "stressed_dscr": round(dscr_stress_rate_150bps, 2),
                    "breaches_covenant": dscr_stress_rate_150bps < COVENANT_MIN_DSCR
                },
                "combined_severe_shock": {
                    "shock": "-10% Revenue drop AND +100 bps rate increase",
                    "stressed_dscr": round(dscr_stress_combined, 2),
                    "breaches_covenant": dscr_stress_combined < COVENANT_MIN_DSCR
                }
            },
            "covenant_breached_under_stress": covenant_breached,
            "mitigations": covenant_mitigations
        },
        "zakat": {
            "methodology": "AAOIFI Adjusted Net Invested Funds (60% zakatable Assets proxy)",
            "zakatable_assets_kwd": round(zakatable_assets, 2),
            "short_term_liabilities_kwd": round(short_term_liabilities, 2),
            "net_zakat_base_kwd": round(net_zakat_base, 2),
            "zakat_due_kwd": round(zakat_due_kwd, 2)
        },
        "purification": {
            "required": purification_required,
            "standard": "AAOIFI Shari'ah Standard No. 21 (Financial Papers) & Standard No. 6",
            "purification_amount_kwd": round(purification_amount_kwd, 2),
            "recommendation": (
                f'Client must purify KWD {purification_amount_kwd:,.2f} of non-compliant interest income by charitable distribution under Shariah Supervisory Board guidance prior to credit facility disbursement.'
                if purification_required else
                'Zero non-compliant interest income detected; no Shariah purification required.'
            )
        }
    }
