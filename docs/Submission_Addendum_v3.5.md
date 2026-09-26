# Submission Addendum v3.5 (attach to the six core documents)

## A. Entity & Commercial Collaboration (challenge: "SME Collaboration Opportunities")
Sanad is presented by [TEAM/COMPANY NAME], a pre-incorporation SME founding team;
Kuwait/UAE entity incorporation is scheduled upon pilot award. We enter this
challenge seeking the commercial collaboration pathway, not only the prize.

| Stage | Model | Indicative pricing (negotiable) |
|---|---|---|
| PoC pilot (3 months, Warba sandbox) | Fixed fee | KWD 4,500 |
| Production licence | Per RM seat / month | KWD 18 / seat |
| Integration, training & support | Annual | 18% of licence value |

## B. Model Risk Management one-pager
- **Intended use:** draft client documentation for human review. NOT a credit-decision
  system; no auto-approval, no client-facing advice without RM release.
- **Components:** deterministic ingestion → BM25 retrieval → dual-mode generation
  (LLM + extractive fallback) → rules-based Shariah/KYC screens → governance layer.
- **Validation:** eval suite v2 — 70+ assertions; citation validity 100%;
  retrieval recall@3 10/10; hash-chained audit log verified by recomputation.
- **Monitoring:** weekly eval run in CI; SCU review-queue aging report; drift log.
- **Fallback SLA:** extractive mode guarantees document availability offline (<5s).
- **Change control:** every export carries a content hash logged in the audit chain.
- **Ownership:** CTO (model) + Shariah Control Unit liaison (rules & opinions).

## C. Executive vocabulary alignment
Open Document 2 with the bank's own language: "a practical AI solution that addresses
specific corporate banking needs" and "open innovation connecting emerging technology
companies with the banking sector" (A. Al-Munaifi, Director of Digital Transformation).
Replace generic "AI-powered platform" phrasing throughout with "practical, deployable
tooling for the corporate front office".

## D. Complementarity with Bdr AI
Bdr AI serves retail mobile customers; Sanad serves the corporate front office.
No overlap: Sanad consumes internal corporate data under RBAC and produces
committee-grade documentation; Bdr remains the consumer-facing agentic assistant.
Joint roadmap option: Sanad-generated insights surfaced in Bdr for corporate clients.

## E. Roadmap addition (Phase 3)
Cross-source conflict detection: flag contradictions between sources
(e.g., registry encumbrance vs silent CRM) and route to RM review queue.

## F. Mobile verification checklist (before submission)
- [ ] KPI strip stacks cleanly at 390px width
- [ ] Tables scroll horizontally without clipping citations
- [ ] WhatsApp/Arabic cards render within viewport
- [ ] Download button reachable without zoom
- [ ] Login gate (when enabled) usable on touch keyboard