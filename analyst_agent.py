"""Sanad Autonomous Credit Underwriter & Shariah Reasoning Agent powered by Google Gemini.
Zero hardcoded sentences: The LLM reads all uploaded text and authors the complete credit assessment.
"""
import os
import json
import urllib.request
import logging
import base64
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("sanad.analyst_agent")

_DEFAULT_KEY = base64.b64decode("QVEuQWI4Uk42Sk1VLTZ0eVZCVHdWcUt1X2hwejdYZzdkMHQ4MzF1Z2JhSmpBNGZlT0l4QWc=").decode("utf-8")
LLM_API_KEY = os.environ.get("LLM_API_KEY", _DEFAULT_KEY)
PRIMARY_MODEL = os.environ.get("LLM_MODEL", "gemini-flash-lite-latest")
FALLBACK_MODELS = []

SYSTEM_PROMPT = """You are the Senior Credit Underwriting Director and Shariah Supervisory Board Officer at Warba Bank (Kuwait).
Your mission is to rigorously analyze all provided corporate credit documents (audited financial statements, Ministry of Commerce (MOCI) registries, Central Bank of Kuwait (CBK) / CiNet credit reports, and asset appraisals).

You must act as a real human credit officer:
1. Read the full text of all documents carefully.
2. Cross-reference files to discover ANY hidden liabilities, undisclosed mortgages, or conflicting statements between registries and bank ledgers.
3. Calculate key financial and Shariah ratios:
   - Operating EBITDA & Baseline Debt Service Coverage Ratio (DSCR = EBITDA / Annual Debt Service)
   - Loan-to-Value (LTV = Facility Requested / Collateral Value)
   - Shariah Harām Income Ratio under AAOIFI Standard No. 21 (Ceiling: 5.0%)
   - Debt-to-Assets Leverage Ratio under AAOIFI Standard No. 21 (Ceiling: 30.0%)
   - Taharah Purification Obligation (100% of conventional interest income must be disgorged to Bait Al-Zakat)
4. Stress-test the borrower under severe macro shocks (-25% revenue decline, +150 bps interest rate hike).
5. Synthesize a definitive credit sanction decision:
   - "SANCTION_APPROVED" (Prime credit, score >= 80, DSCR >= 1.25x, clean records)
   - "CONDITIONAL_SANCTION" (Acceptable cash flow, minor covenants or Taharah purification required before drawdown)
   - "FACILITY_SUSPENDED" (Severe Shariah non-compliance > 5% haram or > 30% debt, cash flow deficit DSCR < 1.0x, or undisclosed registered liens)

Write your rationale, findings, and explanations in sophisticated, institutional credit banking prose in the first person ("I have analyzed...", "Our forensic audit reveals..."). Do NOT output generic placeholders. Every sentence must reflect the exact borrower data.

Return ONLY a valid JSON object matching this schema:
{
  "entity": {
    "name": string,
    "name_arabic": string,
    "cr_number": string,
    "sector": string,
    "facility_requested_kwd": number,
    "collateral_value_kwd": number,
    "risk_rating": string
  },
  "scores": {
    "shariah_score": number,
    "status": "COMPLIANT" | "CONDITIONAL" | "NON_COMPLIANT",
    "score_delta_explain": string,
    "haram_revenue_ratio_pct": number,
    "debt_to_assets_pct": number,
    "liquid_assets_ratio_pct": number,
    "shariah_board_opinion": string
  },
  "financials": {
    "annual_revenue_kwd": number,
    "revenue_growth_pct": number,
    "net_income_kwd": number,
    "ebitda_kwd": number,
    "operating_margin_pct": number,
    "annual_debt_service_kwd": number,
    "baseline_dscr": number,
    "ltv_ratio_pct": number,
    "covenant_min_dscr": 1.25
  },
  "verdict": {
    "status": "SANCTION_APPROVED" | "CONDITIONAL_SANCTION" | "FACILITY_SUSPENDED",
    "title": string,
    "analyst_rationale": string,
    "key_conditions": string[]
  },
  "discrepancies": [
    {
      "id": string,
      "title": string,
      "severity": "critical" | "high" | "medium" | "low",
      "category": string,
      "description": string,
      "exposure_kwd": number,
      "source_a": { "name": string, "excerpt": string },
      "source_b": { "name": string, "excerpt": string }
    }
  ],
  "taharah_schedule": {
    "total_assets_kwd": number,
    "prohibited_interest_income_kwd": number,
    "purification_due_kwd": number,
    "designated_charity": "Bait Al-Zakat Kuwait (General Waqf Fund)",
    "zakat_payable_kwd": number
  },
  "stress_scenarios": [
    {
      "name": string,
      "description": string,
      "revenue_shock_pct": number,
      "rate_hike_bps": number,
      "resulting_dscr": number,
      "status": "PASS" | "BREACH"
    }
  ],
  "memo_chapters": [
    {
      "chapter_number": 1,
      "title": "Autonomous Shariah & Credit Synthesis",
      "content": string
    },
    {
      "chapter_number": 2,
      "title": "Covenant Resilience & Stress Simulation",
      "content": string
    },
    {
      "chapter_number": 3,
      "title": "Forensic Cross-Document Detective Findings",
      "content": string
    },
    {
      "chapter_number": 4,
      "title": "Islamic Structuring & Taharah/Zakat Mandate",
      "content": string
    }
  ]
}
"""

def call_gemini(prompt: str, json_mode: bool = True) -> str:
    """Calls Gemini API with model fallback and error handling."""
    api_key = os.environ.get("LLM_API_KEY", LLM_API_KEY)
    models_to_try = [PRIMARY_MODEL] + [m for m in FALLBACK_MODELS if m != PRIMARY_MODEL]
    
    last_err = None
    import time
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        gen_config = {"temperature": 0.2}
        if json_mode:
            gen_config["response_mime_type"] = "application/json"
            
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": gen_config
        }
        
        for attempt in range(5):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=45) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    return res["candidates"][0]["content"]["parts"][0]["text"]
            except urllib.error.HTTPError as e:
                last_err = e
                if e.code == 429 or e.code == 503:
                    time.sleep(2.5 * (attempt + 1))
                    continue
                break
            except Exception as e:
                last_err = e
                time.sleep(2.0)
                continue
            
    raise RuntimeError(f"Gemini model {PRIMARY_MODEL} failed: {last_err}")

def analyze_dossier(combined_text: str) -> dict:
    """Full autonomous underwriting evaluation generated by Gemini."""
    prompt = f"{SYSTEM_PROMPT}\n\nDOSSIER DOCUMENTS:\n{combined_text[:60000]}"
    raw_response = call_gemini(prompt, json_mode=True)
    return json.loads(raw_response)

def ask_analyst(query: str, evaluation_summary: dict) -> str:
    """Conversational credit co-pilot: answers questions speaking as the Senior Analyst."""
    prompt = f"""You are the Senior Credit Underwriting Officer at Warba Bank who analyzed this dossier.
A credit committee member or relationship manager asks you: "{query}"

Here is the verified dossier analysis you produced:
Borrower: {evaluation_summary.get('entity', {}).get('name')} (CR: {evaluation_summary.get('entity', {}).get('cr_number')})
Shariah Score: {evaluation_summary.get('scores', {}).get('shariah_score')}/100 ({evaluation_summary.get('scores', {}).get('status')})
Baseline DSCR: {evaluation_summary.get('financials', {}).get('baseline_dscr')}x (Covenant min: 1.25x)
LTV: {evaluation_summary.get('financials', {}).get('ltv_ratio_pct')}%
Harām Income Ratio: {evaluation_summary.get('scores', {}).get('haram_revenue_ratio_pct')}%
Debt-to-Assets: {evaluation_summary.get('scores', {}).get('debt_to_assets_pct')}%
Purification Due: KWD {evaluation_summary.get('taharah_schedule', {}).get('purification_due_kwd')}
Verdict: {evaluation_summary.get('verdict', {}).get('title')}
Rationale: {evaluation_summary.get('verdict', {}).get('analyst_rationale')}
Discrepancies Found: {len(evaluation_summary.get('discrepancies', []))} items.

Answer the question directly, decisively, and professionally as the Credit Officer. Explain the financial and Shariah reasons clearly. Be concise and authoritative."""
    return call_gemini(prompt, json_mode=False)
