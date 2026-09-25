"""Source registry + chunking with stable citation IDs (SRC-001#c0)."""
from __future__ import annotations
import json, re
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Chunk:
    chunk_id: str; source_id: str; doc: str; kind: str; text: str

@dataclass
class Source:
    source_id: str; doc: str; kind: str; chunks: list[Chunk] = field(default_factory=list)

DOC_KIND = {"cr_certificate.md":"internal","financials.json":"internal","kyc_status.json":"internal",
            "crm_notes.md":"internal","emails.md":"internal","registry.md":"external","news.md":"external"}

def _chunk_text(text, source_id, doc, kind, max_chars=900):
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    merged, buf = [], ""
    for p in paras:
        buf = f"{buf}\n\n{p}" if buf else p
        if len(buf) >= max_chars: merged.append(buf); buf = ""
    if buf: merged.append(buf)
    return [Chunk(f"{source_id}#c{i}", source_id, doc, kind, m) for i, m in enumerate(merged)]

def load_client(client_dir: Path) -> list[Source]:
    sources = []
    for i, path in enumerate(sorted(client_dir.iterdir())):
        if path.suffix not in (".md", ".json"): continue
        if path.name.startswith("ext_"):   kind = "external"
        elif path.name.startswith("int_"): kind = "internal"
        else:                              kind = DOC_KIND.get(path.name, "internal")
        sid = f"SRC-{i+1:03d}"
        text = path.read_text(encoding="utf-8") if path.suffix == ".md" else json.dumps(json.loads(path.read_text(encoding="utf-8")), indent=2)
        sources.append(Source(sid, path.name, kind,
                              _chunk_text(text, sid, path.name, kind, 1200 if path.suffix==".json" else 900)))
    return sources

def all_chunks(sources): return [c for s in sources for c in s.chunks]