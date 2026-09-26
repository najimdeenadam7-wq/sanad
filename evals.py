"""Sanad eval harness v2 — run: python evals.py
Writes eval_report.md for the submission pack."""
import json, os, shutil, time
from pathlib import Path
import ingest, retrieve, generate, shariah, gaps, structure, governance
from generate import CIT

DATA = Path("data")
CLIENTS = json.loads((DATA/"clients.json").read_text())

EXPECT = {
 "GP-1001": dict(score=100, flags=set(), gaps={("Board Resolution - Credit Facility","MISSING"),
     ("Ultimate Beneficial Ownership Declaration","MISSING")}, cr="214457-2019",
     timeline=7, shareholders=3, zakat_due=29000.0),
 "NS-1002": dict(score=45, flags={"R1 interest income","R2 conventional leverage"},
     gaps={("AML/KYC Screening Report (valid)","EXPIRED")}, cr="118220-2011",
     timeline=6, shareholders=3, zakat_due=134000.0),
 "HM-1003": dict(score=60, flags={"R3 screened activity"},
     gaps={("Audited Financials FY2025","MISSING"),
           ("Ultimate Beneficial Ownership Declaration","MISSING"),
           ("AML/KYC Screening Report (valid)","EXPIRED")}, cr="240981-2016",
     timeline=5, shareholders=3, zakat_due=23500.0),
 "SD-1004": dict(score=100, flags=set(), gaps=set(), cr="305501-2020",
     timeline=6, shareholders=3, zakat_due=20000.0),
}

RETRIEVAL = [
 ("GP-1001","revenue net income margin audited","financials.json"),
 ("GP-1001","shareholders liens registry","registry.md"),
 ("GP-1001","board resolution UBO declaration requested","emails.md"),
 ("NS-1002","conventional term deposit interest income","crm_notes.md"),
 ("NS-1002","mortgage plant conventional bank","registry.md"),
 ("NS-1002","AML screening expired refreshed","emails.md"),
 ("HM-1003","Kuwait Times consumables tender","news.md"),
 ("HM-1003","auditor rotation statements expected","crm_notes.md"),
 ("SD-1004","Wakala deposit surplus cash","crm_notes.md"),
 ("SD-1004","warehousing contract Kuwait Food Union","news.md"),
]

CHECKS = []
def check(name, client, ok, detail=""):
    CHECKS.append([name, client, "PASS" if ok else "FAIL", detail])

total_cites = valid_cites = 0

for cid, meta in CLIENTS.items():
    exp = EXPECT[cid]
    t0 = time.perf_counter()
    sources = ingest.load_client(DATA/cid)
    chunks = ingest.all_chunks(sources)
    known = {c.chunk_id for c in chunks}
    bm = retrieve.BM25(chunks)
    memo = generate.assemble(meta, chunks, bm, use_llm=False)
    screen = shariah.screen(json.loads((DATA/cid/"financials.json").read_text()), chunks)
    gp = gaps.detect(json.loads((DATA/cid/"kyc_status.json").read_text()), meta["name"])
    stt = structure.load(DATA/cid, meta)
    el = time.perf_counter() - t0

    ids = CIT.findall("\n\n".join(s["text"] for s in memo["sections"]))
    total_cites += len(ids); valid_cites += sum(i in known for i in ids)
    check("Citation validity", cid, all(i in known for i in ids), f"{len(ids)} citations")
    check("Every section cited", cid, all(CIT.search(s["text"]) for s in memo["sections"]),
          f"{len(memo['sections'])} sections")
    check("Memo structure", cid, len(memo["sections"]) == 5 and memo["words"] > 50, f"{memo['words']} words")
    check("Shariah flag recall", cid, {f["rule"] for f in screen["flags"]} == exp["flags"],
          f"got {sorted(f['rule'] for f in screen['flags'])}")
    check("Shariah score", cid, screen["score"] == exp["score"], f"got {screen['score']}")
    check("Gap detection exact", cid, {(i["doc"], i["status"]) for i in gp["items"]} == exp["gaps"],
          f"{len(gp['items'])} items")
    check("Outreach email drafted", cid, len(gp["email"]) > 100 and meta["name"] in gp["email"])
    check("Registry CR parsed", cid, stt["profile"].get("CR No.") == exp["cr"], stt["profile"].get("CR No.", ""))
    check("Timeline parsed", cid, len(stt["timeline"]) == exp["timeline"], f"{len(stt['timeline'])} events")
    check("Shareholders parsed", cid, len(stt["shareholders"]) == exp["shareholders"])
    z = shariah.zakat_estimate(json.loads((DATA/cid/"financials.json").read_text()))
    check("Zakat math vs hand-calc", cid, abs(z["zakat_due"] - exp["zakat_due"]) < 1, f"KWD {z['zakat_due']:,.0f}")
    check("Retrieval hits financials", cid,
          any(c.doc == "financials.json" for c in bm.search("revenue net income margin audited", 3)))
    memo2 = generate.assemble(meta, chunks, bm, use_llm=False)
    check("Offline determinism", cid, memo2["sections"] == memo["sections"])
    check("Assembly < 5s", cid, el < 5.0, f"{el:.2f}s")

# Retrieval quality: recall@3 on a designed query set
for rcid, q, want in RETRIEVAL:
    chs = ingest.all_chunks(ingest.load_client(DATA/rcid))
    bmx = retrieve.BM25(chs)
    check(f"Recall@3: {q[:30]}…", rcid, any(c.doc == want for c in bmx.search(q, 3)), f"want {want}")

# Anti-hallucination gate (unit)
gate = generate.sanitize_citations("claim [SRC-999#c9] ok [SRC-001#c0]", {"SRC-001#c0"})
check("Hallucinated cite stripped", "unit", "SRC-999" not in gate and "SRC-001#c0" in gate, gate.strip())

# Governance: tamper-evident audit chain (verified by recomputation)
gov_log = Path("_eval_audit.log")
governance.AUDIT = gov_log
if gov_log.exists(): gov_log.unlink()
governance.log_event("eval", "test_a", "GP-1001", "first")
governance.log_event("eval", "test_b", "NS-1002", "second")
lines = [json.loads(l) for l in gov_log.read_text(encoding="utf-8").strip().splitlines()]
prev, ok_chain = "0"*16, True
for obj in lines:
    payload = json.dumps({k: v for k, v in obj.items() if k != "hash"}, sort_keys=True)
    if governance._chain_hash(prev, payload) != obj["hash"]: ok_chain = False
    prev = obj["hash"]
check("Audit chain tamper-evident", "unit", ok_chain and len(lines) == 2, f"{len(lines)} events")
gov_log.unlink(missing_ok=True)

# Governance: SCU review queue roundtrip
tmp = DATA/"_evaltmp"; tmp.mkdir(exist_ok=True)
governance.save_review("_evaltmp", {"R1 interest income": dict(status="approved", note="ok")})
rq = governance.load_review("_evaltmp")
check("SCU review queue roundtrip", "unit", rq.get("R1 interest income", {}).get("status") == "approved")
shutil.rmtree(tmp, ignore_errors=True)

check("Consent basis metadata", "unit", set(governance.CONSENT_BASIS) >= {"internal","external"})
check("Role model defined", "unit", governance.ROLES == ["rm","credit","scu"])

# Optional: LLM-mode citation gate (runs with ANY provider key)
if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY"):
    cid = "NS-1002"
    chunks = ingest.all_chunks(ingest.load_client(DATA/cid))
    bm = retrieve.BM25(chunks)
    m = generate.assemble(CLIENTS[cid], chunks, bm, use_llm=True)
    known = {c.chunk_id for c in chunks}
    ids = CIT.findall("\n\n".join(s["text"] for s in m["sections"]))
    check("LLM-mode citation validity", cid, all(i in known for i in ids), f"{len(ids)} cites, mode={m['mode']}")
else:
    CHECKS.append(["LLM-mode citation validity", "skipped", "SKIP", "no LLM API key set"])

passed = sum(1 for c in CHECKS if c[2] == "PASS")
failed = sum(1 for c in CHECKS if c[2] == "FAIL")
skipped = sum(1 for c in CHECKS if c[2] == "SKIP")
pct = 100.0 * valid_cites / total_cites if total_cites else 0.0

lines = ["| Check | Client | Result | Detail |", "|---|---|---|---|"]
lines += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in CHECKS]
report = f"""# Sanad Eval Report
Generated: {time.strftime('%Y-%m-%d %H:%M')}
Clients: {len(CLIENTS)} · Checks: {len(CHECKS)} · PASS {passed} · FAIL {failed} · SKIP {skipped}
Citation validity: {pct:.1f}% ({valid_cites}/{total_cites} citations traceable to source chunks)

{chr(10).join(lines)}
"""
Path("eval_report.md").write_text(report)
print(report)
raise SystemExit(1 if failed else 0)