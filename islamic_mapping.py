"""Auto-maps conventional debt structures to Islamic alternatives."""

CONVENTIONAL_TO_ISLAMIC = {
    "overdraft": {
        "islamic_equivalent": "Tawarruq (Commodity Murabaha)",
        "explanation": "Replaces interest-based overdraft with commodity trading structure.",
        "shariah_basis": "AAOIFI Shari'ah Standard No. 30"
    },
    "term_loan": {
        "islamic_equivalent": "Murabaha (Cost-Plus Financing)",
        "explanation": "Bank buys the asset and sells to client at agreed markup.",
        "shariah_basis": "AAOIFI Shari'ah Standard No. 8"
    },
    "equipment_lease": {
        "islamic_equivalent": "Ijarah Muntahia Bittamleek",
        "explanation": "Lease agreement ending with transfer of ownership.",
        "shariah_basis": "AAOIFI Shari'ah Standard No. 9"
    }
}

def suggest_restructuring(conventional_debt_type: str, amount_kwd: float):
    debt_lower = conventional_debt_type.lower()
    for key, mapping in CONVENTIONAL_TO_ISLAMIC.items():
        if key in debt_lower:
            return {
                "flagged_item": conventional_debt_type,
                "amount": amount_kwd,
                "proposed_structure": mapping["islamic_equivalent"],
                "how_it_works": mapping["explanation"],
                "reference": mapping["shariah_basis"]
            }
    return {
        "flagged_item": conventional_debt_type,
        "amount": amount_kwd,
        "proposed_structure": "Tawarruq Working Capital Facility",
        "how_it_works": "Flexible liquidity facility backed by commodity purchases.",
        "reference": "AAOIFI Shari'ah Standard No. 30"
    }