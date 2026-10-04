"""Smart Ingestor: Handles Text PDFs, Scanned PDFs, and Images via Google Vision."""
import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
VISION_CONFIDENCE_THRESHOLD = float(os.environ.get("VISION_CONFIDENCE_THRESHOLD", 0.75))

def _get_vision_client():
    """Lazy load Google Vision client to avoid startup errors if key is missing."""
    try:
        from google.cloud import vision
        return vision.ImageAnnotatorClient()
    except Exception as e:
        print(f"⚠️ Google Vision not configured: {e}")
        return None

def ingest_file(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        return {"error": "File not found", "text": "", "tables": [], "confidence": 0}

    ext = path.suffix.lower()
    
    # 1. Handle Text Files directly (New!)
    if ext in ['.txt', '.md', '.csv', '.json']:
        try:
            text = path.read_text(encoding='utf-8')
            return {"text": text, "tables": [], "confidence": 1.0, "source_type": "text_file"}
        except Exception as e:
            return {"error": str(e), "text": "", "tables": [], "confidence": 0}

    # 1b. Handle Word Documents (.docx)
    if ext == '.docx':
        try:
            import docx
            d = docx.Document(str(path))
            paras = [p.text for p in d.paragraphs if p.text.strip()]
            for table in d.tables:
                for row in table.rows:
                    paras.append(" | ".join(cell.text.strip() for cell in row.cells))
            text = "\n".join(paras)
            return {"text": text, "tables": [], "confidence": 1.0, "source_type": "docx"}
        except Exception as e:
            return {"error": str(e), "text": "", "tables": [], "confidence": 0}

    # 2. Try fast text extraction for PDFs
    if ext == '.pdf':
        text, has_text = _extract_pdf_text(path)
        if has_text and len(text.strip()) > 50:
            return {"text": text, "tables": [], "confidence": 1.0, "source_type": "text_pdf"}
        
        # Scanned PDF fallback via Gemini Multimodal Vision (Zero-cost/builtin fallback)
        gemini_ocr_text = _ocr_with_gemini(path)
        if gemini_ocr_text and len(gemini_ocr_text.strip()) > 10:
            return {"text": gemini_ocr_text, "tables": [], "confidence": 0.95, "source_type": "scanned_pdf_gemini"}
    
    # 3. Google Vision for Scans/Images
    client = _get_vision_client()
    if client:
        return _process_with_vision(client, path, ext)
    else:
        return {"error": "No text layer found", "text": "", "tables": [], "confidence": 0}

def _ocr_with_gemini(path: Path) -> str:
    """Use Gemini Flash Multimodal OCR to extract text from scanned PDFs/images."""
    key = os.environ.get("LLM_API_KEY")
    if not key:
        return ""
    try:
        import urllib.request, json
        model = os.environ.get("LLM_MODEL", "gemini-flash-latest")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        
        with open(path, "rb") as f:
            pdf_bytes = f.read()
        b64_data = base64.b64encode(pdf_bytes).decode("utf-8")
        
        mime_type = "application/pdf" if path.suffix.lower() == ".pdf" else "image/png"
        payload = {
            "contents": [{
                "parts": [
                    {"inlineData": {"mimeType": mime_type, "data": b64_data}},
                    {"text": "Perform complete, high-precision OCR on this document. Extract all text, numbers, tables, line items, headers, signatures, and dates exactly as they appear."}
                ]
            }],
            "generationConfig": {"temperature": 0.0}
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini OCR fallback notice: {e}")
        return ""

def _extract_pdf_text(path: Path):
    """Extract text from standard PDFs."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        text = ""
        has_text = False
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text and page_text.strip():
                has_text = True
                text += page_text + "\n"
        return text, has_text
    except Exception:
        return "", False

def _process_with_vision(client, path: Path, ext: str):
    """OCR and Table extraction using Google Cloud Vision."""
    with open(path, "rb") as image_file:
        content = image_file.read()
    
    image = {"content": content}
    
    # Request both Document Text (OCR) and Tables
    features = [
        {"type_": "DOCUMENT_TEXT_DETECTION"}, # Better for dense text
        {"type_": "TABLE"} # Experimental table feature
    ]
    
    request = {"image": image, "features": features}
    response = client.document_text_detection(request=request) # Use document_text_detection for better OCR
    
    texts = []
    tables = []
    total_confidence = 0
    count = 0

    # Extract Text
    if response.text_annotations:
        # The first annotation is the full text
        full_text = response.text_annotations[0].description
        texts.append(full_text)
        
        # Calculate average confidence from words
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        if word.confidence:
                            total_confidence += word.confidence
                            count += 1

    avg_confidence = (total_confidence / count) if count > 0 else 0.5

    # Note: Table extraction in Vision API is complex and often requires parsing bounding boxes.
    # For this version, we will rely on the LLM to structure the text into tables later.
    # This keeps the code robust and avoids brittle box-parsing logic.

    return {
        "text": "\n".join(texts),
        "tables": tables, # Placeholder for future explicit table parsing
        "confidence": avg_confidence,
        "source_type": "scanned_pdf" if ext == '.pdf' else "image"
    }