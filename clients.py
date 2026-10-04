"""Client registry: scan data/ for portfolios, create new ones, load samples on demand."""
import json, re, subprocess, sys
from pathlib import Path

DATA = Path("data")

def _meta(cid):
    p = DATA/cid/"client_meta.json"
    if p.exists(): return json.loads(p.read_text(encoding="utf-8"))
    legacy = DATA/"clients.json"
    if legacy.exists():
        m = json.loads(legacy.read_text(encoding="utf-8")).get(cid)
        if m: return m
    return {"name": cid, "sector": "—"}

def list_clients():
    if not DATA.exists(): return {}
    return {d.name: _meta(d.name) for d in sorted(DATA.iterdir())
            if d.is_dir() and not d.name.startswith(("_", "."))}

def slugify(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "client"

def create_client(name, sector="", cr=""):
    cid = slugify(name)
    i = 2
    while (DATA/cid).exists():
        cid = f"{slugify(name)}_{i}"; i += 1
    (DATA/cid).mkdir(parents=True, exist_ok=True)
    (DATA/cid/"client_meta.json").write_text(
        json.dumps(dict(name=name, sector=sector or "—", cr=cr), indent=2), encoding="utf-8")
    return cid

def load_samples():
    subprocess.run([sys.executable, "make_synthetic_data.py"], check=True)
    return list_clients()
