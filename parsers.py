"""Parse uploaded files into plain text for ingestion (stdlib-first, optional libs guarded)."""
import csv, io, json

def parse_uploaded(name: str, data: bytes) -> str:
    low = name.lower()
    if low.endswith((".md", ".txt")):
        return data.decode("utf-8", errors="replace")
    if low.endswith(".json"):
        return json.dumps(json.loads(data.decode("utf-8", errors="replace")), indent=2)
    if low.endswith(".csv"):
        rows = list(csv.reader(io.StringIO(data.decode("utf-8", errors="replace"))))
        if not rows: return ""
        return "\n".join(" | ".join(r) for r in rows)
    if low.endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except Exception:
            raise ValueError("PDF support needs: pip install pypdf")
        reader = PdfReader(io.BytesIO(data))
        return "\n\n".join((p.extract_text() or "") for p in reader.pages)
    if low.endswith(".docx"):
        try:
            import docx
        except Exception:
            raise ValueError("DOCX support needs: pip install python-docx")
        d = docx.Document(io.BytesIO(data))
        return "\n\n".join(p.text for p in d.paragraphs if p.text.strip())
    raise ValueError(f"Unsupported file type: {name}")