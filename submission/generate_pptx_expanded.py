import os
import shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_expanded_deck(output_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Executive Theme Colors (Warba Dark Navy + Emerald + Sky Blue)
    c_navy = RGBColor(11, 15, 25)        # #0B0F19 Background
    c_dark_card = RGBColor(18, 25, 45)   # #12192D Card Background
    c_blue = RGBColor(59, 130, 246)      # #3B82F6
    c_emerald = RGBColor(16, 185, 129)   # #10B981
    c_amber = RGBColor(245, 158, 11)     # #F59E0B
    c_red = RGBColor(239, 68, 68)        # #EF4444
    c_purple = RGBColor(168, 85, 247)    # #A855F7
    c_white = RGBColor(255, 255, 255)
    c_slate = RGBColor(148, 163, 184)    # #94A3B8
    c_light_slate = RGBColor(203, 213, 225) # #CBD5E1

    def add_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = c_navy
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category="WARBA BANK CORPORATE BANKING · TRACK 1"):
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11), Inches(0.4))
        tf = cat_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = category.upper()
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = c_blue

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.5), Inches(0.8))
        tf2 = title_box.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = title_text
        p2.font.size = Pt(22)
        p2.font.bold = True
        p2.font.color.rgb = c_white

    def add_card(slide, left, top, width, height, title, items, border_color=c_blue, accent_sub=""):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = c_dark_card
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), height - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = c_white

        if accent_sub:
            p_sub = tf.add_paragraph()
            p_sub.text = accent_sub
            p_sub.font.size = Pt(10)
            p_sub.font.bold = True
            p_sub.font.color.rgb = border_color

        for item in items:
            p_item = tf.add_paragraph()
            p_item.text = f"•  {item}"
            p_item.font.size = Pt(11.5)
            p_item.font.color.rgb = c_light_slate
            p_item.space_before = Pt(5)

    # ==================== SLIDE 1: COVER ====================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1)

    tbox = s1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(3.6))
    tf = tbox.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "WARBA BANK CORPORATE BANKING AI CHALLENGE 2026"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = c_emerald

    p1 = tf.add_paragraph()
    p1.text = "SANAD (سند)"
    p1.font.size = Pt(46)
    p1.font.bold = True
    p1.font.color.rgb = c_white
    p1.space_before = Pt(6)

    p2 = tf.add_paragraph()
    p2.text = "Autonomous Forensic Intelligence & Shariah Underwriting Engine"
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = c_blue
    p2.space_before = Pt(6)

    p3 = tf.add_paragraph()
    p3.text = "Track 1: AI-Powered Client Documentation & Underwriting\nFrom an 11-Day Manual Friction into a 38-Second Perfected Credit Dossier"
    p3.font.size = Pt(14)
    p3.font.color.rgb = c_light_slate
    p3.space_before = Pt(14)

    meta_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.1), Inches(11.3), Inches(1.5))
    meta_card.fill.solid()
    meta_card.fill.fore_color.rgb = c_dark_card
    meta_card.line.color.rgb = c_blue

    mtb = s1.shapes.add_textbox(Inches(1.2), Inches(5.2), Inches(10.9), Inches(1.3))
    mtf = mtb.text_frame
    mtf.word_wrap = True
    mp = mtf.paragraphs[0]
    mp.text = "🌐 Live Production Web App: https://sanad-engine.netlify.app"
    mp.font.size = Pt(13)
    mp.font.bold = True
    mp.font.color.rgb = c_white

    mp2 = mtf.add_paragraph()
    mp2.text = "⚡ High-Availability Backend API: https://sanad-production-9d51.up.railway.app/health\n📂 Public GitHub Repository: https://github.com/anajimdeen01-debug/sanad-frontend\n📜 Standard Adherence: AAOIFI Standards No. 21 & 35 | Central Bank of Kuwait (CBK) Risk Covenants"
    mp2.font.size = Pt(10.5)
    mp2.font.color.rgb = c_slate
    mp2.space_before = Pt(4)

    # ==================== SLIDE 2: THE PROBLEM ====================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2)
    add_header(s2, "The Core Problem: Anatomy of the 11-Day Underwriting Bottleneck")

    add_card(s2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
             "Fragmented Dossiers", 
             ["Relationship Managers spend 65% of working hours chasing and reconciling 70+ pages of PDF filings.",
              "Audited balance sheets, MOCI extracts, and letters reviewed across disjointed operational silos.",
              "Creates 8–14 day turnaround delays where high-velocity corporate borrowers are poached by rivals."],
             border_color=c_amber, accent_sub="Manual Status Quo")

    add_card(s2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
             "Isolated OCR Blind Spots", 
             ["Conventional OCR tools analyze files in isolation without multi-source circularization.",
              "Completely miss contradictions between credit declarations and official court gazettes.",
              "Undisclosed performance bonds and affiliate debentures slip into sanctioned facilities."],
             border_color=c_red, accent_sub="Hidden Liquidation Risk")

    add_card(s2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
             "Manual Shariah Scrubbing", 
             ["Shariah teams must manually comb line-by-line through P&L 'Other Income' footnotes.",
              "Conventional deposit interest income requires legally binding Taharah purification.",
              "Manual Zakat and purification math creates governance friction before drawdown."],
             border_color=c_blue, accent_sub="Governance Delay")

    # ==================== SLIDE 3: SYSTEM ARCHITECTURE OVERVIEW ====================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3)
    add_header(s3, "System Architecture: End-to-End 5-Pillar Operating Engine")

    add_card(s3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.3),
             "Pillar 1: Sovereign Ingestion & Redaction",
             ["Multi-file ingestion (PDF, Word, Excel, scanned tables).",
              "On-premise regex & NER redactor strips Kuwait Civil IDs and PII.",
              "Ensures 100% compliance with CBK data sovereignty rules."],
             border_color=c_blue, accent_sub="Zero Data Leakage")

    add_card(s3, Inches(6.8), Inches(1.8), Inches(5.6), Inches(2.3),
             "Pillar 2: Adversarial Circularization",
             ["Cross-examines applicant claims against external registers.",
              "Integrates MOCI Commercial Registry & CiNet Credit Bureau.",
              "Surfaces undisclosed guarantees & conflicting encumbrances."],
             border_color=c_red, accent_sub="Discrepancy Hunter")

    add_card(s3, Inches(0.8), Inches(4.4), Inches(5.6), Inches(2.3),
             "Pillar 3: AAOIFI Shariah Core",
             ["Automated screening under AAOIFI Standard No. 21 (<5% income).",
              "Calculates exact Taharah purification dividend down to the fil.",
              "Pre-drafts electronic transfer voucher to Bait Al-Zakat Kuwait."],
             border_color=c_emerald, accent_sub="Deterministic Purification")

    add_card(s3, Inches(6.8), Inches(4.4), Inches(5.6), Inches(2.3),
             "Pillar 4 & 5: Documentation & RM Radar",
             ["Client Documentation Studio: Auto-generates CAM, Term Sheet, RM Brief.",
              "Live Covenant Stress: -25% revenue shock & +150 bps rate simulations.",
              "Proactive RM Radar: Uncovers +KWD 700k expansion opportunities."],
             border_color=c_purple, accent_sub="Front-Office Enabler")

    # ==================== SLIDE 4: DEEP DIVE PILLAR 1 ====================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4)
    add_header(s4, "Pillar 1: Sovereign Data Redaction & Ingestion Pipeline")

    add_card(s4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "How Ingestion Operates",
             ["Multi-Format Parser: Handles PDF scans, Excel financial models, Word charters, and MOCI extracts concurrently.",
              "Instant CR Intake: Relationship Managers can enter a Kuwait Commercial Registration number (e.g. 204918-KW) to immediately pull pre-circularized telemetry.",
              "Table Structure Preservation: Accurately parses multi-period balance sheets, cash flow schedules, and footnote notes without losing column hierarchy."],
             border_color=c_blue, accent_sub="Universal Input Layer")

    add_card(s4, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "CBK Sovereign Privacy Shield (Why Unique)",
             ["On-Premise PII Scrubbing: Strips sensitive Kuwait Civil IDs, private telephone numbers, and residential addresses prior to LLM processing.",
              "Air-Gapped Compliance: Eliminates cross-border sovereign data leakage, adhering strictly to Central Bank of Kuwait (CBK) data sovereignty directives.",
              "Cryptographic Provenance: Generates SHA-256 document fingerprints ensuring the ingested document has not been tampered with post-upload."],
             border_color=c_emerald, accent_sub="Regulatory Compliance")

    # ==================== SLIDE 5: DEEP DIVE PILLAR 2 ====================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5)
    add_header(s5, "Pillar 2: Adversarial Forensic Circularization & Conflict Detection")

    add_card(s5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "How It Operates (Adversarial Checking)",
             ["Cross-Document Verification: Treats every borrower statement as an adversarial claim that must be corroborated by independent official records.",
              "Automated Circularization: Simultaneously cross-references loan application affidavits, audited financial footnotes (Notes 14, 18, 22), MOCI registration certificates, and Central Bank (CiNet) bureau reports.",
              "Conflict Exposure Quantification: Calculates the exact monetary exposure in KWD associated with each contradiction."],
             border_color=c_amber, accent_sub="Multi-Source Intelligence")

    add_card(s5, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Autonomous Legal Remediation (How It Does It)",
             ["Automated Covenant Generation: When an undisclosed liability is caught (e.g. sister-company bond), SANAD does not merely reject the file.",
              "Synthesis of Legal Armor: Automatically drafts the exact protective Condition Precedent: 'Borrower must execute an irrevocable Priority & Subordination Deed ranking Warba Bank senior to affiliate debenture.'",
              "1-Click Evidence Grounding: Committee members click citation pills to view the verbatim conflicting document excerpts side-by-side."],
             border_color=c_red, accent_sub="Defensive Structuring")

    # ==================== SLIDE 6: DEEP DIVE PILLAR 3 ====================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6)
    add_header(s6, "Pillar 3: AAOIFI Shariah Core & Autonomous Taharah Purification")

    add_card(s6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "AAOIFI Standard No. 21 Screening",
             ["Footnote Scanning: Screens P&L schedules and 'Other Income' footnotes for conventional bank interest and non-halal sub-lease income.",
              "Prohibited Income Test: Prohibited Income ÷ Total Revenue must remain < 5.0% (e.g. Gulf Pearl Foods = 0.09% PASS; Qabas Trading = 8.40% BREACH).",
              "Debt-to-Assets Leverage Test: Conventional Interest-Bearing Debt ÷ Total Assets must remain < 30.0% (e.g. Gulf Pearl = 22.4% PASS; Qabas = 42.5% BREACH).",
              "Liquid Assets Floor: Evaluates cash and liquid instruments against the 33.0% minimum threshold."],
             border_color=c_emerald, accent_sub="Financial Papers Standard")

    add_card(s6, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Deterministic Taharah & Zakat Calculation",
             ["100% Disgorgement Mandate: 100% of non-compliant earnings are isolated down to the fil for purification (Taharah).",
              "Bait Al-Zakat Remittance Voucher: Pre-drafts electronic remittance voucher designating Bait Al-Zakat Kuwait (General Waqf Fund) as beneficiary.",
              "AAOIFI Standard No. 35 (Zakat): Calculates the Zakatable base using the step-down proxy (60% of total assets) and applies the 2.577% solar Zakat factor.",
              "Zero Shariah Friction: Transforms a multi-week Shariah Board review into an instant, deterministic sign-off."],
             border_color=c_blue, accent_sub="Standard No. 35 Zakat")

    # ==================== SLIDE 7: DEEP DIVE PILLAR 4 ====================
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7)
    add_header(s7, "Pillar 4: Financial Analytics & Live Covenant Stress Simulator")

    add_card(s7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Cash Flow Velocity & Ratio Engine",
             ["Normalized Operating EBITDA: Filters out non-recurring gains to establish true sustainable cash flow.",
              "Debt Service Coverage Ratio (DSCR): Calculated dynamically as Operating EBITDA ÷ Total Annual Debt Service commitments.",
              "Covenant Floor Enforcement: Enforces Warba Bank's strict 1.25x minimum DSCR policy threshold.",
              "Loan-to-Value (LTV): Evaluates facility size against certified real estate or asset appraisal backing (Policy ceiling: 80.0%).",
              "Cash Conversion Forensics: Computes Days Sales Outstanding (DSO) and compares against industry benchmarks."],
             border_color=c_blue, accent_sub="Core Banking Formulas")

    add_card(s7, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Real-Time Macroeconomic Stress Simulator",
             ["Interactive Underwriting Sliders: Allows committee members to simulate stress scenarios live during committee deliberations.",
              "Shock 1 (-15% to -25% Revenue Downturn): Models sector-wide supply chain disruptions and margin compression.",
              "Shock 2 (+150 to +250 bps Rate Hike): Models Central Bank of Kuwait (CBK) discount rate tightening pass-through.",
              "Combined Crisis Simulation: Simultaneously stresses revenue by -20% and benchmark rates by +250 bps to verify capital survival.",
              "Immediate Visual Feedback: Recharts bar visualizer displays resulting DSCR against the 1.25x floor instantly."],
             border_color=c_amber, accent_sub="Committee Decision Tool")

    # ==================== SLIDE 8: TRACK 1 CLIENT DOCUMENTATION ====================
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8)
    add_header(s8, "Track 1 Core Deliverable: Client Documentation Studio")

    add_card(s8, Inches(0.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "Credit Memo (CAM)",
             ["Warba Bank Corporate Credit Committee executive format.",
              "Transaction appraisal, historical revenue growth, operating margin, and DSCR velocity.",
              "Footnote citations linked to SHA-256 verification hashes."],
             border_color=c_blue, accent_sub="Official Bank Template")

    add_card(s8, Inches(3.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "Murabaha Term Sheet",
             ["Binding financing agreement terms (Commodity Murabaha / Tawarruq).",
              "Margin pricing: CBK Discount Rate + 2.25% p.a. (Profit floor 5.50%).",
              "Mandatory covenants: Min 1.25x DSCR & 1st-degree collateral lien."],
             border_color=c_emerald, accent_sub="Financing Contract")

    add_card(s8, Inches(6.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "RM Executive Brief",
             ["1-page commercial cheat-sheet for front-office relationship bankers.",
              "Key negotiation talking points and operating strengths.",
              "Expansion upsell triggers: +KWD 700k expansion & trade LC financing."],
             border_color=c_amber, accent_sub="Front-Office Enabler")

    add_card(s8, Inches(9.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "SSB Taharah Memo",
             ["Shariah Supervisory Board endorsement packet.",
              "AAOIFI Standards 21 & 35 compliance certificate.",
              "Pre-drafted Bait Al-Zakat donation voucher ready prior to drawdown."],
             border_color=c_purple, accent_sub="Shariah Endorsement")

    # ==================== SLIDE 9: CASE STUDY ====================
    s9 = prs.slides.add_slide(blank_layout)
    add_bg(s9)
    add_header(s9, "Real-World Forensic Audit: Gulf Pearl Foods (CR #204918-KW)")

    add_card(s9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "The Deception: Undisclosed Performance Bond",
             ["The Borrower Claim: In Credit Application Clause 5.2, company asserted 'Zero Contingent Liabilities & Zero Affiliate Guarantees'.",
              "The Forensic Discovery: SANAD's automated circularization scanned Ministry of Justice Gazette Vol 44 and uncovered an active KWD 350,000 corporate bond issued to sister entity Pearl Logistics.",
              "The Liquidation Risk: In insolvency, this hidden guarantee would dilute Warba Bank's ranking as senior secured creditor.",
              "The Evidence Trail: Directly binds credit committee to Gazette Entry 18 and Balance Sheet Note 14."],
             border_color=c_red, accent_sub="Discrepancy Ref #F-922")

    add_card(s9, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "The Automated Remediation: Protective Covenant",
             ["Condition Precedent: SANAD synthesized a mandatory Condition Precedent for the credit agreement:",
              "'Borrower must execute an irrevocable Priority & Subordination Deed ranking Warba Bank facility senior to affiliate guarantee.'",
              "Shariah Purification: Detected KWD 7,900 conventional interest in Note 7; drafted transfer order to Bait Al-Zakat.",
              "Outcome: Prevents KWD 350,000 credit impairment while closing the facility in 38 seconds."],
             border_color=c_emerald, accent_sub="Autonomous Legal Armor")

    # ==================== SLIDE 10: PROACTIVE RM RADAR ====================
    s10 = prs.slides.add_slide(blank_layout)
    add_bg(s10)
    add_header(s10, "Front-Office Growth: Proactive RM Revenue Radar")

    add_card(s10, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Turnaround Velocity",
             ["11 Days → 38 Seconds",
              "94% reduction in manual document synthesis time.",
              "Accelerates credit approval turnaround from 2 weeks to same-day review.",
              "Allows Warba Bank to capture prime commercial borrowers first."],
             border_color=c_blue, accent_sub="Time-to-Yes Advantage")

    add_card(s10, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Balance-Sheet Expansion",
             ["+KWD 700K Facility Upsell",
              "Detected unencumbered liquid inventory cushion of KWD 1.2M.",
              "Recommended +KWD 700k Murabaha facility expansion (DSCR 3.80x safe).",
              "Generates +KWD 39,375 net profit margin annually for Warba Bank."],
             border_color=c_emerald, accent_sub="RM Revenue Radar")

    add_card(s10, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Trade Finance Cross-Sell",
             ["Import LC & FX Hedging",
              "Analyzed supplier import ledgers from Southeast Asian suppliers.",
              "Pre-drafted proposal for Import Letters of Credit (LCs) and FX forward lines.",
              "Expands fee income wallet share while deepening client loyalty."],
             border_color=c_amber, accent_sub="Wallet-Share Growth")

    # ==================== SLIDE 11: COMPETITIVE ADVANTAGE ====================
    s11 = prs.slides.add_slide(blank_layout)
    add_bg(s11)
    add_header(s11, "Competitive Advantage: Why SANAD Is Uniquely Defensible")

    add_card(s11, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Why Generic GenAI & OCR Fail in Banking",
             ["Generic GenAI (ChatGPT/Claude): Evaluates single prompts in isolation, suffers from hallucinations, lacks mathematical precision, and leaks sensitive PII to public clouds.",
              "Legacy OCR (ABBYY/Kofax): Simply digitizes paper into text or raw tables. Zero adversarial circularization, zero understanding of Shariah standards, and zero ability to draft covenants.",
              "Legacy Core Systems (Finacle): Pure transaction ledgers; unable to interpret unstructured legal gazettes or perform forensic audits."],
             border_color=c_red, accent_sub="Existing Technological Limits")

    add_card(s11, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "The SANAD Moat: Uniquely Built for Warba Bank",
             ["Adversarial Multi-Source Circularization: The only engine that actively hunts contradictions between credit declarations and external registries.",
              "Deterministic AAOIFI Taharah Engine: Solves Islamic banking's biggest friction by automating purification math down to the fil.",
              "CBK Sovereign Privacy Shield: On-premise sanitization ensures zero regulatory air-gap breaches.",
              "Cryptographic Governance Ledger: SHA-256 and Merkle root block height verify institutional auditability."],
             border_color=c_emerald, accent_sub="Institutional Defensibility")

    # ==================== SLIDE 12: EVALUATION PROTOCOL ====================
    s12 = prs.slides.add_slide(blank_layout)
    add_bg(s12)
    add_header(s12, "Production Readiness: Live Demo & 60-Second Evaluation Protocol")

    add_card(s12, Inches(0.8), Inches(1.8), Inches(11.6), Inches(4.8),
             "Test the Live Production Application Directly",
             [
               "🌐 Live Production Web App: https://sanad-engine.netlify.app",
               "⚡ Live Backend API: https://sanad-production-9d51.up.railway.app",
               "📂 GitHub Code Repository: https://github.com/anajimdeen01-debug/sanad-frontend",
               " ",
               "STEP-BY-STEP EVALUATION GUIDE FOR JUDGES (60 SECONDS):",
               "1. Open Gulf Pearl Foods Trading (CR #204918-KW) from the main directory.",
               "2. Read the 4 AI Forensic Chapters authored dynamically by Google Gemini.",
               "3. Click citation [#F-922: Undisclosed Bond] to inspect the document provenance modal.",
               "4. Click '⚡ Re-Analyze with Gemini' to watch live unscripted reasoning in real-time.",
               "5. Slide the Revenue Stress slider to -25% and observe real-time DSCR recalculation.",
               "6. Switch to 'Client Documentation Studio' to inspect the CAM, Term Sheet, and RM Brief.",
               "7. Click 'Sign as Analyst' and 'Sign as SCU' to record cryptographic governance endorsements."
             ],
             border_color=c_emerald, accent_sub="Live Evaluation Protocol")

    prs.save(output_path)
    print(f"Expanded PPTX saved to: {output_path}")

if __name__ == '__main__':
    out_dir = r"c:\Users\DELL-PC\sanad-v2\submission"
    os.makedirs(out_dir, exist_ok=True)
    out_pptx = os.path.join(out_dir, "SANAD_Executive_Presentation_Deck_Warba_Bank.pptx")
    build_expanded_deck(out_pptx)

    # Also update original filename if not locked
    orig_pptx = os.path.join(out_dir, "SANAD_Pitch_Deck_Warba_Bank.pptx")
    try:
        shutil.copy2(out_pptx, orig_pptx)
        print(f"Also updated: {orig_pptx}")
    except Exception as e:
        print(f"Notice: {orig_pptx} is currently open in PowerPoint. Check {out_pptx}")
