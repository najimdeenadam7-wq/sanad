"""Writes a ready-to-upload test pack under test_pack/ + guided test script."""
from pathlib import Path

P = Path("test_pack")
P.mkdir(exist_ok=True)

FILES = {
 "ext_news_tobacco.md": """2026-09-20 Al-Rai: Gulf Pearl Foods signs cigarette logistics agreement
Gulf Pearl Foods Trading W.L.L. has signed a three-year distribution and cold-storage agreement
with Kuwait Tobacco Manufacturing Co., covering cigarette logistics for the Gulf market,
per a company statement released on 2026-09-20.
Analysts note the revenue share from this line is undisclosed.""",

 "int_board_resolution.md": """BOARD RESOLUTION - Gulf Pearl Foods Trading W.L.L.
Dated 2026-09-28, Shuwaikh Head Office.
The board authorises the CEO to negotiate and execute a Murabaha facility
up to KWD 1,800,000 with Warba Bank K.S.C. for working-capital purposes.
The CFO is authorised to provide all documentation required by the bank.
Signed: Fahad Al-Otaibi (Chairman), Khalid Al-Otaibi (CFO).""",

 "ext_bureau_novasteel.csv": """metric,value,as_of
credit_bureau_score,612,2026-08-31
total_bank_facilities_kwd,7400000,2026-08-31
overdue_instances_24m,1,2026-08-31
court_cases,0,2026-08-31
bounced_cheques_12m,2,2026-08-31""",

 "int_meeting_notes_hilal.txt": """2026-09-22 Call notes - Hilal Medical Supplies
RM Omar Al-Rashidi spoke with the CEO re MOH tender execution.
Utilisation of current limit 55%; no overdue in 24 months.
Client requests extension of invoice-financing tenor to 150 days
to match the MOH payment cycle; offers MOH contract assignment as security.""",
}

SCRIPT = """# Guided localhost test script (test_pack/)
Run: streamlit run ui.py   then follow in order. EXPECTED = pass.

1. Select GP-1001 -> Assemble.
   EXPECT: Shariah 100/100, Citations KPI = 7, gaps = 2.
2. Sidebar upload: ext_news_tobacco.md as EXTERNAL.
   EXPECT: auto re-assemble; Shariah score drops to 60; R3 flag 'tobacco';
   SCU review queue shows 1 item; appendix gains an external row for this file.
3. Upload int_board_resolution.md as INTERNAL.
   EXPECT: appendix gains internal row; memo section 5 cites it.
   NOTE: gaps table unchanged on purpose - KYC status is a system-of-record
   field; in the pilot it syncs from the bank's checklist API.
4. Switch to NS-1002 -> upload ext_bureau_novasteel.csv as EXTERNAL.
   EXPECT: CSV parsed; appendix excerpt shows 'metric | value | as_of';
   Risk section cites bureau rows (overdue instances, bounced cheques).
5. Switch to HM-1003 -> upload int_meeting_notes_hilal.txt as INTERNAL.
   EXPECT: 'utilisation 55%' and '150 days' appear in cited memo text.
6. Approve & Export: tick RM + Credit + SCU -> Download.
   EXPECT: filename hash differs from previous download; audit trail shows
   upload / assemble / approve / export_version events with chained hashes.
7. Sidebar -> Remove uploaded sources (back on GP-1001).
   EXPECT: score returns to 100; appendix back to 7 citations.

Demo-Day stunt: do step 2 LIVE on stage - drop a news PDF on an open client
and watch the Shariah score move in front of the judges.
"""

for name, text in FILES.items():
    (P/name).write_text(text, encoding="utf-8")
(P/"TEST_SCRIPT.md").write_text(SCRIPT, encoding="utf-8")
print(f"✔ test pack written to {P}/ ({len(FILES)} documents + TEST_SCRIPT.md)")