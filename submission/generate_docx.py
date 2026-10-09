import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def create_docx(output_path):
    doc = Document()

    # Set page margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Styles
    title_p = doc.add_paragraph()
    r_cat = title_p.add_run("WARBA BANK CORPORATE BANKING AI CHALLENGE 2026 · TRACK 1\n")
    r_cat.font.name = "Calibri"
    r_cat.font.size = Pt(11)
    r_cat.font.bold = True
    r_cat.font.color.rgb = RGBColor(16, 185, 129)

    r_title = title_p.add_run("SANAD (سند)\n")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(28)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(11, 15, 25)

    r_sub = title_p.add_run("Autonomous Forensic Intelligence & Shariah Underwriting Engine\n")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(16)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(59, 130, 246)

    r_desc = title_p.add_run("Transforming Corporate Client Documentation from an 11-Day Friction into a 38-Second Perfected Dossier")
    r_desc.font.name = "Calibri"
    r_desc.font.size = Pt(12)
    r_desc.font.color.rgb = RGBColor(100, 116, 139)

    # Meta Table
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.cell(0, 0)
    set_cell_background(cell, "F1F5F9")
    cp = cell.paragraphs[0]
    r = cp.add_run(
        "🌐 Live Production Web App: https://sanad-engine.netlify.app\n"
        "⚡ Live Backend API: https://sanad-production-9d51.up.railway.app/health\n"
        "📂 Public GitHub Repository: https://github.com/anajimdeen01-debug/sanad-frontend"
    )
    r.font.name = "Calibri"
    r.font.size = Pt(10)
    r.font.bold = True

    doc.add_page_break()

    # Sections
    sections = [
        ("1. The Core Problem in Corporate Underwriting", [
            ("Fragmented Dossiers (70+ Pages)", "Relationship Managers spend 65% of their working hours manually reconciling balance sheets, MOCI commercial registries, and credit letters across disconnected silos. Results in 8–14 day delays."),
            ("Hidden Liquidation Liens", "Conventional OCR tools analyze documents in isolation. They miss contradictions between credit declarations and Ministry of Justice gazettes, allowing undisclosed performance bonds and affiliate guarantees to slip through."),
            ("Manual Shariah Scrubbing", "Shariah review teams must comb line-by-line through P&L 'Other Income' footnotes to isolate conventional deposit interest and calculate mandatory Taharah purification math.")
        ]),
        ("2. The Solution: SANAD System Architecture", [
            ("Adversarial Forensic Circularization", "Concurrently ingests audited financials, CiNet bureau reports, MOCI registries, and PACI data. The Discrepancy Hunter runs cross-statement verification algorithms to compare claimed liabilities against official gazettes."),
            ("Sovereign Data Privacy Shield", "Client PII is sanitized on-premise in strict accordance with Central Bank of Kuwait (CBK) data sovereignty regulations prior to analytical processing."),
            ("AAOIFI Shariah & Taharah Engine", "Calculates conventional income ratios (<5% ceiling) and debt-to-assets (<30% ceiling) under AAOIFI Standard No. 21. Automatically computes exact dividend purification down to the fil and drafts Bait Al-Zakat transfer orders."),
            ("Covenant Stress Modeling", "Runs Monte Carlo stress testing under -25% revenue shocks and +150 bps discount rate hikes, checking DSCR resilience against the 1.25x Warba Bank policy floor.")
        ]),
        ("3. Track 1 Core Deliverable: Client Documentation Studio", [
            ("Credit Application Memo (CAM)", "Full institutional memorandum tailored to Warba Bank Corporate Credit Committee with revenue velocity, DSCR, and grounded footnote citations."),
            ("Murabaha Term Sheet", "Binding financing agreement terms (Commodity Murabaha / Tawarruq), margin pricing (CBK Discount Rate + 2.25%), and covenant undertakings."),
            ("Relationship Manager Proactive Brief", "1-page front-office commercial cheat-sheet with talking points, operational velocity metrics, and pre-identified upsell expansion triggers (+KWD 700k)."),
            ("Shariah Supervisory Board (SSB) Memo", "Official endorsement memo under AAOIFI Standards 21 and 35 with pre-drafted Bait Al-Zakat donation vouchers prior to drawdown.")
        ]),
        ("4. Forensic Case Study: Gulf Pearl Foods Trading W.L.L. (CR #204918-KW)", [
            ("The Deception", "In Credit Application Clause 5.2, company asserted 'Zero Contingent Liabilities & Zero Affiliate Guarantees'."),
            ("The Forensic Discovery (Ref #F-922)", "SANAD circularized the filing against the Ministry of Justice Legal Gazette (Vol 44, Entry 18) and uncovered an active KWD 350,000 corporate performance bond issued to sister entity Pearl Logistics."),
            ("The Automated Remediation", "SANAD automatically drafted a mandatory Condition Precedent: 'Borrower must execute an irrevocable Priority & Subordination Deed ranking Warba Bank facility senior to affiliate guarantee.' Prevents KWD 350,000 credit impairment.")
        ]),
        ("5. Commercial Impact & ROI for Warba Bank", [
            ("94% Turnaround Reduction", "Compresses underwriting turnaround from 11 business days to 38 seconds, allowing Warba Bank to capture high-velocity commercial deals first."),
            ("+KWD 700,000 Balance Sheet Expansion", "Identified KWD 1.2M unencumbered liquid inventory cushion, triggering a +KWD 700k facility upsell that generates +KWD 39,375 net profit margin annually."),
            ("Cryptographic Audit Ledger", "Every footnote citation is bound to a SHA-256 hash and Merkle root block height with sequential 3-tier digital governance sign-offs.")
        ]),
        ("6. Self-Guided 60-Second Evaluation Protocol for Judges", [
            ("Step 1", "Open Gulf Pearl Foods Trading (CR #204918-KW) from https://sanad-engine.netlify.app."),
            ("Step 2", "Review the 4 AI Forensic Chapters authored dynamically by Google Gemini with AAOIFI standards."),
            ("Step 3", "Click citation [#F-922: Undisclosed Bond] to inspect the document provenance modal."),
            ("Step 4", "Click '⚡ Re-Analyze with Gemini' to watch unscripted AI reasoning live in real-time."),
            ("Step 5", "Drag the Revenue Stress slider to -25% and observe real-time DSCR recalculation."),
            ("Step 6", "Switch to 'Client Documentation Studio' to inspect the CAM, Term Sheet, and RM Brief."),
            ("Step 7", "Click 'Sign as Analyst' to append digital cryptographic governance endorsement.")
        ])
    ]

    for title, items in sections:
        h = doc.add_heading(level=1)
        r = h.add_run(title)
        r.font.name = "Calibri"
        r.font.color.rgb = RGBColor(15, 23, 42)

        for item_title, item_desc in items:
            p = doc.add_paragraph()
            r_it = p.add_run(f"• {item_title}: ")
            r_it.font.name = "Calibri"
            r_it.font.bold = True
            r_it.font.color.rgb = RGBColor(59, 130, 246)

            r_id = p.add_run(item_desc)
            r_id.font.name = "Calibri"
            r_id.font.color.rgb = RGBColor(51, 65, 85)

        doc.add_paragraph()

    doc.save(output_path)
    print(f"DOCX saved to: {output_path}")

if __name__ == '__main__':
    out_dir = r"c:\Users\DELL-PC\sanad-v2\submission"
    os.makedirs(out_dir, exist_ok=True)
    out_docx = os.path.join(out_dir, "SANAD_Pitch_Deck_Warba_Bank.docx")
    create_docx(out_docx)
