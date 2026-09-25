# Sanad (سند) — AI Client File Engine
**Warba Bank Corporate Banking AI Challenge 2026 · Track 1: AI-Powered Client Documentation**

Citation-first credit-memo assembly with Shariah pre-screening, Zakat estimation,
KYC gap detection, and an RM briefing card. Every claim carries a source citation.

## Quickstart
    pip install -r requirements.txt
    python make_synthetic_data.py
    streamlit run ui.py            # works fully offline (extractive mode)

## Optional LLM prose (any provider)
    # NVIDIA NIM (free):  build.nvidia.com -> API Keys
    set OPENAI_API_KEY=nvapi-...                      # base URL + model default to NVIDIA
    # or Anthropic:       set ANTHROPIC_API_KEY=sk-ant-...
    # or local Ollama:    set OPENAI_BASE_URL=http://localhost:11434/v1 && set OPENAI_API_KEY=ollama
    # or Groq/OpenRouter: set OPENAI_BASE_URL + OPENAI_MODEL accordingly

## Eval suite
    python evals.py                # writes eval_report.md (attach to submission)

## Docker / deploy
    docker build -t sanad . && docker run -p 8501:8501 sanad
    # or push to GitHub -> Render Web Service (auto-detects Dockerfile)

## Architecture
Ingest (immutable chunk IDs) -> BM25 retrieval -> dual-mode generation with
mandatory citations + anti-hallucination gate -> Shariah rules screen + Zakat
estimate -> KYC gap detection + outreach -> structured UI + approved export.
Pilot extension points: pypdf/docx parsers, pgvector embeddings, core-banking
APIs, RBAC/SSO, immutable audit log, private/self-hosted LLM endpoint.