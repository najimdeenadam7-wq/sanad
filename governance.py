"""Governance layer: tamper-evident audit log, Shariah Control Unit review queue,
consent/licence metadata, export versioning, role model."""
import hashlib, json, time
from pathlib import Path

DATA = Path("data")
AUDIT = DATA / "audit.log"

ROLES = ["rm", "credit", "scu"]
DEMO_USERS = {"rm": "sanad-rm-2026", "credit": "sanad-credit-2026", "scu": "sanad-scu-2026"}

CONSENT_BASIS = {
    "internal": "Client consent under banking agreement + internal policy (demo: synthetic)",
    "external": "Licensed / public feed terms (demo: synthetic extract)",
}

def _chain_hash(prev: str, payload: str) -> str:
    return hashlib.sha256((prev + payload).encode()).hexdigest()[:16]

def last_hash() -> str:
    if not AUDIT.exists(): return "0" * 16
    lines = AUDIT.read_text(encoding="utf-8").strip().splitlines()
    if not lines: return "0" * 16
    try: return json.loads(lines[-1])["hash"]
    except Exception: return "0" * 16

def log_event(user: str, action: str, client: str, detail: str = ""):
    DATA.mkdir(exist_ok=True)
    payload = json.dumps(dict(ts=time.strftime("%Y-%m-%d %H:%M:%S"), user=user,
                              action=action, client=client, detail=detail), sort_keys=True)
    h = _chain_hash(last_hash(), payload)
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(dict(json.loads(payload), hash=h)) + "\n")
    return h

def read_audit(n: int = 20):
    if not AUDIT.exists(): return []
    out = []
    for line in AUDIT.read_text(encoding="utf-8").strip().splitlines()[-n:]:
        try: out.append(json.loads(line))
        except Exception: pass
    return out

def load_review(cid: str) -> dict:
    p = DATA / cid / "shariah_review.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

def save_review(cid: str, review: dict):
    (DATA / cid / "shariah_review.json").write_text(json.dumps(review, indent=2), encoding="utf-8")