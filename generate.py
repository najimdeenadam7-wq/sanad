"""Citation-first memo assembly.
LLM prose via Anthropic OR any OpenAI-compatible endpoint (NVIDIA NIM, Groq,
OpenRouter, local Ollama). No key? Extractive fallback — grouped per source,
always works, zero cost."""
import json as _json
import os, re, urllib.request

CIT = re.compile(r"\[(SRC-\d+#c\d+)\]")

SECTIONS = [
 ("overview","1. Client Overview & Relationship History",
   ["company registration capital signatories","relationship history meetings RM","shareholders registry liens"]),
 ("financials","2. Financial Performance & Position",
   ["revenue net income margin audited","total assets equity interest bearing debt","gross margin auditor opinion"]),
 ("risk","3. Risk Factors & Mitigants",
   ["utilisation overdue conduct","news market prices volatility","mortgage liens collateral"]),
 ("shariah","4. Shariah Compliance Screen",
   ["interest income conventional deposit","insurance stake screened activity","debt assets conventional bank"]),
 ("recommendation","5. Facility Recommendation & Next Steps",
   ["facility limit increase renewal request","missing documents board resolution UBO","tender contract expansion next steps"]),
]

def _snippet(c, n=280):
    return c.text if len(c.text) <= n else c.text[:n].rsplit(" ", 1)[0] + "…"

def _prompt(client, title, picked):
    body = "\n".join(f"{c.chunk_id}: {c.text}" for c in picked)
    return (f"You are a senior corporate credit analyst at Warba Bank (Islamic bank, Kuwait).\n"
            f"Write section '{title}' of a credit memo for client {client['name']}.\n"
            f"Use ONLY the chunks below. Cite EVERY claim with its chunk id in square brackets, e.g. [SRC-002#c0].\n"
            f"Max 180 words. Banker prose or bullets. State uncertainty explicitly; never invent figures.\n"
            f"CHUNKS:\n{body}")

def _anthropic(prompt):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key: return None
    try:
        import anthropic
        r = anthropic.Anthropic(api_key=key).messages.create(
            model=os.environ.get("SANAD_MODEL", "claude-sonnet-4-5"), max_tokens=600,
            messages=[{"role": "user", "content": prompt}])
        return r.content[0].text
    except Exception:
        return None

def _openai_compat(prompt):
    """Any OpenAI-compatible API: NVIDIA NIM (default), Groq, OpenRouter, Ollama."""
    key = os.environ.get("OPENAI_API_KEY")
    if not key: return None
    base  = os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1")
    model = os.environ.get("OPENAI_MODEL", "meta/llama-3.3-70b-instruct")
    try:
        req = urllib.request.Request(
            base.rstrip("/") + "/chat/completions",
            data=_json.dumps({"model": model, "temperature": 0.2, "max_tokens": 600,
                              "messages": [{"role": "user", "content": prompt}]}).encode(),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            out = _json.loads(resp.read().decode())
        return out["choices"][0]["message"]["content"]
    except Exception:
        return None

def sanitize_citations(text, known):
    """Anti-hallucination gate: strip any citation not in the retrieved set."""
    return CIT.sub(lambda m: m.group(0) if m.group(1) in known else "", text)

def _extractive(picked):
    """Offline fallback, grouped per source document for judge-readable output."""
    if not picked: return "_No relevant sources retrieved for this section._"
    by_doc = {}
    for c in picked:
        by_doc.setdefault(c.doc, []).append(c)
    out = []
    for doc, cs in by_doc.items():
        out.append(f"**{doc}**")
        out += [f"- {_snippet(c)} [{c.chunk_id}]" for c in cs]
    return "\n".join(out)

def assemble(client, chunks, bm, use_llm=True):
    sections, llm_used, fallbacks = [], 0, 0
    known = {c.chunk_id for c in chunks}
    for sid, title, queries in SECTIONS:
        picked = []
        for q in queries:
            for c in bm.search(q, 3):
                if c.chunk_id not in {p.chunk_id for p in picked}: picked.append(c)
        picked = picked[:6]
        text = None
        if use_llm:
            p = _prompt(client, title, picked)
            text = _anthropic(p) or _openai_compat(p)
        if text: llm_used += 1
        else:
            fallbacks += 1
            text = _extractive(picked)
        text = sanitize_citations(text, known)
        sections.append(dict(id=sid, title=title, text=text.strip()))
    cites = list(dict.fromkeys(CIT.findall("\n\n".join(s["text"] for s in sections))))
    words = sum(len(s["text"].split()) for s in sections)
    mode = "llm" if fallbacks == 0 else ("hybrid" if llm_used else "extractive")
    return dict(sections=sections, citations=cites, words=words, mode=mode)