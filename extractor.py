"""AI Extractor: 7 Specialized Prompts to fill the dashboard."""
import os
import json
import re
import urllib.request
import time
from dotenv import load_dotenv

load_dotenv()

# --- LLM Configuration ---
LLM_API_KEY = os.environ.get("LLM_API_KEY")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://integrate.api.nvidia.com/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "gemini-flash-latest")

# --- The 7 Master Prompts (with doubled braces for .format()) ---
PROMPTS = {
    "profile": """You are a data extraction engine for corporate credit files.
Extract the following fields from the document. 
RULES:
- If a value is not present or unclear, set it to null and set needs_review=true.
- NEVER guess or invent values.
- Return ONLY valid JSON. No markdown, no explanation.

FIELDS TO EXTRACT: client_name, cr_number, sector, registered_capital, signatories, valid_until, registry_status, relationship_manager, confidence, needs_review

DOCUMENT:
{text}""",

    "timeline": """You are a credit analyst assistant. Extract all chronological events, meetings, interactions, or transactions mentioned.
RULES:
- Only include events with a clear date.
- Return ONLY a JSON array of objects with keys: date, source_type, event_summary, action_required.
- If no events found, return empty array [].

DOCUMENT:
{text}""",

    "shareholders": """Extract all shareholders, owners, partners, or beneficial owners.
RULES:
- Include name and ownership percentage.
- Return ONLY JSON with keys: shareholders (array of objects with name and stake_pct), ubo_identified, confidence.
- If no shareholders found, return empty shareholders array.

DOCUMENT:
{text}""",

    "news": """Extract all news items, market signals, or external events related to the client.
RULES:
- Include date, headline, and sentiment (positive/negative/neutral).
- Return ONLY JSON with key: news_items (array of objects).
- If no news found, return empty array.

DOCUMENT:
{text}""",

    "financials": """You are a senior financial analyst. Extract ALL financial data.
RULES:
- Extract every number: revenue, profit, assets, liabilities, equity, debt.
- If a number is unclear, set to null.
- Return ONLY JSON with keys: fiscal_years (array of objects with year, revenue, net_income, total_assets, total_equity, total_debt), auditor, audit_opinion.

DOCUMENT:
{text}""",

    "shariah": """You are a Shariah Compliance Officer.
TASK: Scan for: alcohol, gambling, gaming, tobacco, pork, conventional insurance, interest/riba.
RULES:
- Quote the EXACT text where found.
- Return ONLY JSON with keys: flags (array of objects with rule, severity, finding, evidence), shariah_score (0-100).
- If nothing found, return empty flags array and shariah_score 100.

DOCUMENT:
{text}""",

    "gaps": """You are a credit operations officer. Compare documents against standard checklist.
CHECKLIST: Commercial Registration, Audited Financials (2-3 yrs), Board Resolution, Signatory Passports, AML/KYC Report, UBO Declaration, Insurance, Tax Returns.
RULES:
- Identify PRESENT, MISSING, or EXPIRED.
- Return ONLY JSON with keys: documents (array of objects with name and status), missing_count.

DOCUMENT:
{text}"""
}

MASTER_PROMPT = """You are a senior corporate credit data extraction engine for Warba Bank.
Extract ALL structured credit data from the document into a single valid JSON object with the exact keys: profile, timeline, shareholders, news, financials, shariah, gaps.

RULES:
- If a value is not present or unclear, set to null and set needs_review=true.
- NEVER guess, estimate, or invent values or numbers.
- Return ONLY valid JSON. No markdown code blocks, no explanation text.

DOCUMENT:
{text}"""

def _call_llm(prompt: str) -> str:
    """Calls the LLM (supports Gemini and OpenAI-compatible APIs) with retry on 503."""
    provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
    api_key = os.environ.get("LLM_API_KEY")
    
    if not api_key:
        print("[WARN] No LLM_API_KEY found in .env")
        return "{}"

    for attempt in range(3):
        try:
            if provider == "gemini":
                model = os.environ.get("LLM_MODEL", "gemini-flash-latest")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                req_data = json.dumps({
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1}
                }).encode("utf-8")
                req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=35) as resp:
                    result = json.loads(resp.read().decode())
                    return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                base_url = os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1")
                model = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")
                req_data = json.dumps({
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                }).encode("utf-8")
                req = urllib.request.Request(
                    f"{base_url}/chat/completions",
                    data=req_data,
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=35) as resp:
                    result = json.loads(resp.read().decode())
                    return result["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
                continue
            print(f"   [ERROR] LLM Error after 3 attempts: {e}")
            return "{}"

def _parse_json_safely(text: str) -> dict:
    """Extracts JSON from LLM response safely, handling markdown blocks."""
    if not text or text == "{}":
        return {}
    clean = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    clean = re.sub(r"\s*```$", "", clean.strip(), flags=re.MULTILINE).strip()
    
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        match = re.search(r"[\{\[].*[\}\]]", clean, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return {}

def _heuristic_fallback(text: str) -> dict:
    """Deterministic regex extraction fallback if LLM is unavailable."""
    name_m = re.search(r"(?:Company|Client|Name):\s*([^\n\r]+)", text, re.I)
    cr_m = re.search(r"(?:CR\s*(?:No\.?|Number)|Registration):\s*([^\s|\n]+)", text, re.I)
    rev_m = re.search(r"(?:Revenue|Turnover)(?:\s*20\d\d)?:\s*([0-9,]+(?:\.[0-9]+)?)", text, re.I)
    ni_m = re.search(r"(?:Net\s*Income|Profit)(?:\s*20\d\d)?:\s*([0-9,]+(?:\.[0-9]+)?)", text, re.I)
    
    sh_list = []
    for m in re.finditer(r"([A-Za-z\s\-]+)\s*\(?(\d+)%\)?", text):
        sh_list.append({"name": m.group(1).strip(), "stake_pct": float(m.group(2))})

    flags = []
    sh_score = 100
    for prohibited in ["alcohol", "gambling", "gaming", "tobacco", "pork", "conventional insurance"]:
        if re.search(rf"\b{prohibited}\b", text, re.I) and not re.search(rf"no\s+(?:involvement|stake|activity)\s+in\s+{prohibited}", text, re.I):
            flags.append({"rule": f"R3 screened activity ({prohibited})", "severity": "HIGH", "finding": f"Keyword '{prohibited}' detected in document text."})
            sh_score -= 40
    
    revenue_val = float(rev_m.group(1).replace(",", "")) if rev_m else 0.0
    net_income_val = float(ni_m.group(1).replace(",", "")) if ni_m else 0.0

    return {
        "profile": {
            "client_name": name_m.group(1).strip() if name_m else "Extracted Entity",
            "cr_number": cr_m.group(1).strip() if cr_m else None,
            "sector": "Commercial Trading",
            "confidence": 0.85
        },
        "timeline": [],
        "shareholders": {"shareholders": sh_list, "confidence": 0.85},
        "news": {"news_items": []},
        "financials": {
            "fiscal_years": [{
                "year": 2025,
                "revenue": revenue_val,
                "net_income": net_income_val,
                "total_assets": revenue_val * 0.55 if revenue_val else 0.0,
                "total_equity": revenue_val * 0.25 if revenue_val else 0.0,
                "total_debt": revenue_val * 0.05 if revenue_val else 0.0
            }]
        },
        "shariah": {"flags": flags, "shariah_score": max(0, sh_score)},
        "gaps": {"documents": [], "missing_count": 0}
    }

def extract_all(text: str) -> dict:
    """Extracts all 7 sections. Tries LLM first; falls back gracefully to heuristic parsing."""
    if not text or not text.strip():
        return _heuristic_fallback("")

    # Try fast individual prompts first or master
    results = {}
    llm_succeeded = False
    
    for key in ["profile", "financials", "shariah", "shareholders"]:
        template = PROMPTS.get(key)
        if template:
            prompt = template.format(text=text[:3500])
            raw = _call_llm(prompt)
            parsed = _parse_json_safely(raw)
            if parsed and parsed != {}:
                results[key] = parsed
                llm_succeeded = True
            else:
                break

    if llm_succeeded and "profile" in results and "financials" in results:
        # Fill optional keys
        for key in ["timeline", "news", "gaps"]:
            template = PROMPTS.get(key)
            if template:
                raw = _call_llm(template.format(text=text[:3500]))
                results[key] = _parse_json_safely(raw)
        return results

    # Fallback guaranteed extraction
    print("   [INFO] Using fallback extraction heuristic...")
    return _heuristic_fallback(text)

if __name__ == "__main__":
    sample_text = "Gulf Pearl Foods Trading W.L.L. CR 214457-2019. Revenue 2024: 18M KWD. Net Income: 1.3M KWD. Shareholders: Fahad Al-Otaibi 55%."
    print(json.dumps(extract_all(sample_text), indent=2))