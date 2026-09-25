"""Generates a realistic synthetic client portfolio under data/."""
import json
from pathlib import Path

DATA = Path("data")

CLIENTS = {
 "GP-1001": dict(name="Gulf Pearl Foods Trading W.L.L.",
  sector="Import & distribution of frozen and dry foods",
  files={
  "cr_certificate.md": """COMMERCIAL REGISTRATION - STATE OF KUWAIT
Company: Gulf Pearl Foods Trading W.L.L.
CR No.: 214457-2019 | PACI: 390114457
Activity: Import & distribution of frozen and dry foods
Registered capital: KWD 450,000 (fully paid)
Signatories: Fahad Al-Otaibi (CEO); joint with CFO above KWD 50,000
Valid until: 2027-03-31""",
  "financials.json": {"client":"Gulf Pearl Foods Trading W.L.L.","fy2025":{"revenue_kwd":18400000,"net_income_kwd":1310000,"total_assets_kwd":9600000,"total_equity_kwd":4100000,"interest_bearing_debt_kwd":900000,"interest_income_pct":0.0,"gross_margin_pct":14.2,"auditor":"Al-Muzaffar & Co - clean opinion"},"fy2024":{"revenue_kwd":16100000,"net_income_kwd":1020000}},
  "kyc_status.json": {"present":["Commercial Registration Certificate","Signatory Passport Copies","Audited Financials FY2024","Audited Financials FY2025","AML/KYC Screening Report (valid)","Insurance Coverage Summary"],"expired":[]},
  "crm_notes.md": """RELATIONSHIP HISTORY - Gulf Pearl Foods
RM: Sara Al-Hamad (since 2021)
2026-06-14 Meeting at client HQ: discussed KWD 1.2M working-capital Murabaha limit for cold-store expansion in Shuwaikh; client to provide UBO declaration.
2026-07-02 Call: CFO confirmed supply contract with Sultan Center Group renewed for 3 years (est. KWD 6.5M/yr).
2026-08-19 Internal: limit utilisation 78%; no overdue days in 24 months; account conduct satisfactory.
2026-09-08 Meeting: client requests increase of Murabaha limit to KWD 1.8M; mentioned competing quote from NBK.""",
  "emails.md": """2026-09-09 Inbound - CFO Khalid Al-Otaibi: attached FY2025 audited statements; UBO declaration to follow next week.
2026-09-10 Outbound - RM: requested board resolution authorising limit increase.
2026-09-15 Inbound - CFO: board meets 2026-09-28; resolution expected 2026-09-30.""",
  "news.md": """2026-05-11 Al-Anbaa: Gulf Pearl Foods commissions 4,000 sqm cold-chain facility in Shuwaikh Industrial Area.
2026-08-03 Meed: Kuwaiti food distributors report margin pressure from freight costs; Gulf Pearl among few with own logistics fleet.""",
  "registry.md": """Kuwait Companies Registry extract (external source):
Gulf Pearl Foods Trading W.L.L. - CR 214457-2019, status ACTIVE.
Shareholders: Fahad Al-Otaibi 55%, Khalid Al-Otaibi 30%, Pearl Gulf Holdings W.L.L. 15%.
No registered liens or judgments as of 2026-09-01."""}) ,
 "NS-1002": dict(name="NovaSteel Industries K.S.C.",
  sector="Steel manufacturing & contracting",
  files={
  "cr_certificate.md": """COMMERCIAL REGISTRATION - STATE OF KUWAIT
Company: NovaSteel Industries K.S.C.
CR No.: 118220-2011 | Activity: Steel manufacturing & contracting
Registered capital: KWD 2,000,000 | Valid until: 2028-01-15""",
  "financials.json": {"client":"NovaSteel Industries K.S.C.","fy2025":{"revenue_kwd":41200000,"net_income_kwd":2870000,"total_assets_kwd":13100000,"total_equity_kwd":5200000,"interest_bearing_debt_kwd":5400000,"interest_income_pct":8.4,"gross_margin_pct":11.9,"auditor":"BDO Al-Nibari & Co - clean opinion"},"fy2024":{"revenue_kwd":37800000,"net_income_kwd":2310000}},
  "kyc_status.json": {"present":["Commercial Registration Certificate","Signatory Passport Copies","Board Resolution - Credit Facility","Audited Financials FY2024","Audited Financials FY2025","AML/KYC Screening Report (valid)","Ultimate Beneficial Ownership Declaration","Insurance Coverage Summary"],"expired":["AML/KYC Screening Report (valid)"]},
  "crm_notes.md": """RELATIONSHIP HISTORY - NovaSteel
2026-08-01 Relationship transferred from RM Ahmed Z. to RM Laila M.; handover notes incomplete, context reconstructed from emails.
2026-08-22 Meeting: client seeks renewal of KWD 4.0M facility maturing 2026-11-30 and addition of LC sub-limit.
2026-09-05 Internal: utilisation 91%; one technical overdue day in Feb-2026 (ops error, waived).
2026-09-12 Call: CFO disclosed idle cash parked in conventional term deposit yielding the reported interest income.""",
  "emails.md": """2026-09-06 Inbound - CFO: renewal application + FY2025 audited statements attached.
2026-09-07 Outbound - RM: requested refreshed AML screening (previous report expired Feb-2026).""",
  "news.md": """2026-04-22 Meed: NovaSteel awards KWD 9.8M EPC subcontract for Gulf logistics hub project.
2026-07-30 Reuters: regional steel prices volatile on import duties; Kuwaiti mills partially shielded by local demand.""",
  "registry.md": """Kuwait Companies Registry extract (external source):
NovaSteel Industries K.S.C. - CR 118220-2011, status ACTIVE.
Shareholders: Al-Fahad Family Holding 61%, GCC Steel Partners 27%, public free float 12%.
Registered mortgage over Shuwaikh plant in favour of a conventional bank (2024)."""}),
 "HM-1003": dict(name="Hilal Medical Supplies Co. K.S.C.",
  sector="Medical supplies distribution; minority stake in conventional insurance brokerage",
  files={
  "cr_certificate.md": """COMMERCIAL REGISTRATION - STATE OF KUWAIT
Company: Hilal Medical Supplies Co. K.S.C.
CR No.: 240981-2016 | Activity: Medical supplies distribution
Registered capital: KWD 800,000 | Valid until: 2027-09-30""",
  "financials.json": {"client":"Hilal Medical Supplies Co. K.S.C.","fy2025":{"revenue_kwd":12700000,"net_income_kwd":940000,"total_assets_kwd":6400000,"total_equity_kwd":2900000,"interest_bearing_debt_kwd":600000,"interest_income_pct":0.0,"gross_margin_pct":18.3,"auditor":"EY Al-Aiban & Co - clean opinion"},"fy2024":{"revenue_kwd":10900000,"net_income_kwd":760000}},
  "kyc_status.json": {"present":["Commercial Registration Certificate","Signatory Passport Copies","Board Resolution - Credit Facility","Audited Financials FY2024","Insurance Coverage Summary"],"expired":["AML/KYC Screening Report (valid)"]},
  "crm_notes.md": """RELATIONSHIP HISTORY - Hilal Medical
RM: Omar Al-Rashidi (since 2023)
2026-07-21 Meeting: client won KWD 3.1M Ministry of Health tender; requests invoice-financing via Tawarruq structure.
2026-08-30 Call: FY2025 audit delayed by auditor rotation; statements expected 2026-10-15.
2026-09-10 Internal: exposure within appetite; tender cash-cycle gap approx 120 days.""",
  "emails.md": """2026-09-11 Inbound - CEO: MOH award letter attached as tender evidence.
2026-09-14 Outbound - RM: requested FY2025 audited statements, refreshed AML screen and UBO declaration.""",
  "news.md": """2026-06-18 Kuwait Times: Hilal Medical Supplies awards KWD 3.1M Ministry of Health tender for consumables.
2026-03-09 Mubasher: Hilal Medical Supplies holds 22% stake in Gulf Shield Conventional Insurance Broker K.S.C., acquired 2024.""",
  "registry.md": """Kuwait Companies Registry extract (external source):
Hilal Medical Supplies Co. K.S.C. - CR 240981-2016, status ACTIVE.
Shareholders: Al-Rashidi Medical Holdings 58%, GCC Health Ventures 20%, Gulf Shield Conventional Insurance Broker 22% cross-holding.
No registered liens as of 2026-09-01."""}) ,
 "SD-1004": dict(name="Sadaf Cold Chain Logistics K.S.C.",
  sector="Refrigerated logistics & warehousing",
  files={
  "cr_certificate.md": """COMMERCIAL REGISTRATION - STATE OF KUWAIT
Company: Sadaf Cold Chain Logistics K.S.C.
CR No.: 305501-2020 | Activity: Refrigerated logistics & warehousing
Registered capital: KWD 1,200,000 | Valid until: 2029-05-31
Signatories: Mona Al-Sabah (CEO); dual signature with CFO above KWD 25,000""",
  "financials.json": {"client":"Sadaf Cold Chain Logistics K.S.C.","fy2025":{"revenue_kwd":9800000,"net_income_kwd":1150000,"total_assets_kwd":8000000,"total_equity_kwd":3600000,"interest_bearing_debt_kwd":400000,"interest_income_pct":0.0,"gross_margin_pct":22.4,"auditor":"KPMG Al-Safi & Co - clean opinion"},"fy2024":{"revenue_kwd":8600000,"net_income_kwd":940000}},
  "kyc_status.json": {"present":["Commercial Registration Certificate","Signatory Passport Copies","Board Resolution - Credit Facility","Audited Financials FY2024","Audited Financials FY2025","AML/KYC Screening Report (valid)","Ultimate Beneficial Ownership Declaration","Insurance Coverage Summary"],"expired":[]},
  "crm_notes.md": """RELATIONSHIP HISTORY - Sadaf Cold Chain
RM: Huda Al-Farsi (since 2022)
2026-05-04 Meeting: client requests KWD 2.5M Murabaha facility for fleet expansion (12 refrigerated trucks).
2026-06-11 Call: CFO confirmed utilisation 42%; account conduct fully satisfactory.
2026-08-14 Meeting: discussed Wakala deposit placement for surplus cash.
2026-09-09 Internal: annual review scheduled; file complete per checklist.""",
  "emails.md": """2026-09-10 Inbound - CFO: board resolution for facility request attached.
2026-09-16 Outbound - RM: confirmation of complete file; credit committee slot booked.""",
  "news.md": """2026-04-30 Meed: Sadaf Cold Chain wins 3-year warehousing contract with Kuwait Food Union.
2026-07-22 Al-Qabas: cold-chain capacity in Kuwait tight; Sadaf adds 12-truck refrigerated fleet.""",
  "registry.md": """Kuwait Companies Registry extract (external source):
Sadaf Cold Chain Logistics K.S.C. - CR 305501-2020, status ACTIVE.
Shareholders: Sadaf Holdings K.S.C. 52%, Gulf Refrigeration Partners W.L.L. 28%, Kuwait Logistics Fund 20%.
No security interests registered as of 2026-09-01."""}) ,
}

REQUIRED = ["Commercial Registration Certificate","Signatory Passport Copies",
 "Board Resolution - Credit Facility","Audited Financials FY2024","Audited Financials FY2025",
 "AML/KYC Screening Report (valid)","Ultimate Beneficial Ownership Declaration","Insurance Coverage Summary"]

if __name__ == "__main__":
    (DATA).mkdir(exist_ok=True)
    (DATA/"required_docs.json").write_text(json.dumps(REQUIRED, indent=2))
    index = {}
    for cid, c in CLIENTS.items():
        d = DATA/cid; d.mkdir(parents=True, exist_ok=True)
        for fname, content in c["files"].items():
            (d/fname).write_text(content if isinstance(content, str) else json.dumps(content, indent=2))
        index[cid] = dict(name=c["name"], sector=c["sector"])
    (DATA/"clients.json").write_text(json.dumps(index, indent=2))
    print(f"✔ synthetic portfolio written to {DATA}/ ({len(CLIENTS)} clients)")