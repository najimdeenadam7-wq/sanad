"""Generates real-looking banking documents under real_pack/ for upload testing."""
import json
from pathlib import Path

P = Path("real_pack")
P.mkdir(exist_ok=True)

# ---------- 1. Audited financial statements (real .docx via python-docx) ----------
def make_docx():
    try:
        from docx import Document
        from docx.shared import Pt
    except Exception:
        (P/"NovaSteel_Audited_FS_FY2025.md").write_text(
            "# Independent Auditor's Report (docx unavailable - markdown fallback)\n"
            "See real_pack guide.", encoding="utf-8")
        return
    d = Document()
    h = d.add_heading("BDO Al-Nibari & Co.", 0)
    d.add_paragraph("Chartered Accountants · Kuwait City · Al-Soor Tower, 14th Floor")
    d.add_heading("Independent Auditor's Report to the Shareholders of NovaSteel Industries K.S.C.", 1)
    d.add_paragraph(
        "Opinion: We have audited the financial statements of NovaSteel Industries K.S.C. (the "
        "\"Company\"), which comprise the statement of financial position as at 31 December 2025, and the "
        "statements of income, changes in equity and cash flows for the year then ended, and notes to the "
        "financial statements, including a summary of significant accounting policies. In our opinion, the "
        "accompanying financial statements present fairly, in all material respects, the financial position "
        "of the Company as at 31 December 2025, and its financial performance and its cash flows for the year "
        "then ended in accordance with IFRS as issued by the IASB.")
    d.add_heading("Statement of Financial Position (KWD)", 2)
    t = d.add_table(rows=1, cols=3); t.style = "Light Grid Accent 1"
    hdr = t.rows[0].cells
    hdr[0].text = "Line item"; hdr[1].text = "FY2025"; hdr[2].text = "FY2024"
    for row in [("Total assets", "13,100,000", "12,300,000"),
                ("Total equity", "5,200,000", "4,800,000"),
                ("Interest-bearing debt", "5,400,000", "5,700,000"),
                ("Revenue", "41,200,000", "37,800,000"),
                ("Net income for the year", "2,870,000", "2,310,000")]:
        c = t.add_row().cells
        c[0].text, c[1].text, c[2].text = row
    d.add_heading("Notes to the financial statements", 2)
    d.add_paragraph(
        "Note 14 - Borrowings: The Company carries a conventional term loan of KWD 5,400,000 with a "
        "conventional bank, maturing 2028, priced at CBK discount rate plus 2.5%. The loan is secured by a "
        "mortgage over the Shuwaikh plant.")
    d.add_paragraph(
        "Note 22 - Other income: Interest income of KWD 3,460,800 (8.4% of revenue) arose from surplus cash "
        "placed on conventional term deposits during the year.")
    d.add_paragraph("Engagement partner: Y. Al-Nibari · Licence 118-F · Report dated 2026-03-15")
    d.save(str(P/"NovaSteel_Audited_FS_FY2025.docx"))

# ---------- 2. Credit bureau report (CSV) ----------
(P/"NovaSteel_Bureau_Report_Q3_2026.csv").write_text(
"""report_id,metric,value,as_of
NB-2026-Q3-88121,credit_bureau_score,612,2026-08-31
NB-2026-Q3-88121,total_bank_facilities_kwd,7400000,2026-08-31
NB-2026-Q3-88121,overdue_instances_24m,2,2026-08-31
NB-2026-Q3-88121,court_cases,1,2026-08-31
NB-2026-Q3-88121,bounced_cheques_12m,2,2026-08-31
NB-2026-Q3-88121,utilisation_pct,91,2026-08-31
NB-2026-Q3-88121,oldest_facility_opened,2019-04-01,2026-08-31""", encoding="utf-8")

# ---------- 3. Board resolution (letterhead MD) ----------
(P/"NovaSteel_Board_Resolution_2026-09.md").write_text(
"""NOVASTEEL INDUSTRIES K.S.C.
Board of Directors · Resolution No. 07/2026 · Passed 2026-09-20, Kuwait City

PRESENT: Mr. Talal Al-Fahad (Chairman), Mr. Bader Al-Mutairi, Ms. Haya Al-Salem, Mr. Yousef Kanakso
QUORUM: Confirmed by Company Secretary per Article 24 of the Articles of Association.

IT WAS RESOLVED THAT:
1. The Company's credit facility with Warba Bank K.S.C. (KWD 4,000,000, maturing 2026-11-30)
   be renewed on terms to be negotiated by the Chief Financial Officer.
2. The Chairman and the CFO, acting jointly, are authorised to execute all facility
   documentation, including any Islamic restructuring instruments offered by the Bank.
3. The Board notes management's request to refinance the existing conventional term loan
   (Note 14 of the FY2025 audited financial statements) and mandates management to evaluate
   Shariah-compliant alternatives presented by the Bank.
4. This resolution remains valid for twelve months from the date of passing.

Signed: Talal Al-Fahad (Chairman) · Haya Al-Salem (Director) · Company Secretary seal affixed.""", encoding="utf-8")

# ---------- 4. AML/KYC screening report (TXT) ----------
(P/"Hilal_AML_Screening_Report.txt").write_text(
"""KUWAIT CLEARING COMPANY K.S.C. - AML / KYC SCREENING REPORT
Report reference: AML-2025-02-0144          Issued: 2025-02-14
Subject entity: Hilal Medical Supplies Co. K.S.C. (CR 240981-2016)
Validity: 12 months from issue date (lapsed 2026-02-14)

SCREENING SCOPE: UN Consolidated List, US OFAC SDN, EU Sanctions, UK HMT,
Kuwait MOJ designated lists, adverse media (Arabic + English), PEP database.

RESULTS:
- Sanctions matches: 0 (zero) exact or fuzzy matches requiring escalation.
- PEP matches: 1 fuzzy match (shareholder name similarity 82%) - reviewed and
  cleared as false positive by compliance officer N. Al-Awadi, ref CP-2025-0091.
- Adverse media: 2 articles relating to a civil payment dispute with a supplier,
  settled out of court 2024-12-03; no criminal dimension identified.
- Beneficial ownership: