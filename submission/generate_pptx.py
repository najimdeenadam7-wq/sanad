import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Colors
    c_navy = RGBColor(11, 15, 25)        # #0B0F19
    c_dark_card = RGBColor(18, 25, 45)   # #12192D
    c_blue = RGBColor(59, 130, 246)      # #3B82F6
    c_emerald = RGBColor(16, 185, 129)   # #10B981
    c_amber = RGBColor(245, 158, 11)     # #F59E0B
    c_white = RGBColor(255, 255, 255)
    c_slate = RGBColor(148, 163, 184)    # #94A3B8
    c_light_slate = RGBColor(203, 213, 225)

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
            p_sub.font.color.rgb = border_color

        for item in items:
            p_item = tf.add_paragraph()
            p_item.text = f"•  {item}"
            p_item.font.size = Pt(12)
            p_item.font.color.rgb = c_light_slate
            p_item.space_before = Pt(6)

    # ==================== SLIDE 1: COVER ====================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1)

    tbox = slide1_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(3.5))
    tf = tbox.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "WARBA BANK CORPORATE BANKING AI CHALLENGE 2026"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = c_emerald

    p1 = tf.add_paragraph()
    p1.text = "SANAD (سند)"
    p1.font.size = Pt(48)
    p1.font.bold = True
    p1.font.color.rgb = c_white
    p1.space_before = Pt(8)

    p2 = tf.add_paragraph()
    p2.text = "Autonomous Forensic Intelligence & Shariah Underwriting Engine"
    p2.font.size = Pt(22)
    p2.font.color.rgb = c_blue
    p2.space_before = Pt(6)

    p3 = tf.add_paragraph()
    p3.text = "Track 1: AI-Powered Client Documentation & Underwriting\nFrom an 11-Day Manual Bottleneck to a 38-Second Perfected Credit Dossier"
    p3.font.size = Pt(14)
    p3.font.color.rgb = c_light_slate
    p3.space_before = Pt(16)

    meta_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.2), Inches(11.3), Inches(1.3))
    meta_card.fill.solid()
    meta_card.fill.fore_color.rgb = c_dark_card
    meta_card.line.color.rgb = c_blue

    mtb = s1.shapes.add_textbox(Inches(1.2), Inches(5.35), Inches(10.9), Inches(1.0))
    mtf = mtb.text_frame
    mtf.word_wrap = True
    mp = mtf.paragraphs[0]
    mp.text = "🌐 Live Production Web App: https://sanad-engine.netlify.app"
    mp.font.size = Pt(13)
    mp.font.bold = True
    mp.font.color.rgb = c_white

    mp2 = mtf.add_paragraph()
    mp2.text = "⚡ Backend API: https://sanad-production-9d51.up.railway.app | Code: https://github.com/anajimdeen01-debug/sanad-frontend"
    mp2.font.size = Pt(11)
    mp2.font.color.rgb = c_slate

    # ==================== SLIDE 2: THE PROBLEM ====================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2)
    add_header(s2, "The Core Problem: The 11-Day Underwriting Bottleneck")

    add_card(s2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
             "Fragmented Dossiers", 
             ["Relationship Managers spend 65% of working hours chasing 70+ pages of PDF filings.",
              "Audited balance sheets, MOCI extracts, and letters reviewed in disjointed silos.",
              "Creates 8–14 day turnaround delays where high-velocity clients are lost to rivals."],
             border_color=c_amber, accent_sub="Manual Status Quo")

    add_card(s2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
             "Hidden Liquidation Liens", 
             ["Conventional OCR tools analyze files in isolation without cross-checking.",
              "Completely miss contradictions between application claims and court gazettes.",
              "Undisclosed performance bonds and sister-company debentures slip through."],
             border_color=RGBColor(239, 68, 68), accent_sub="Blind-Spot Risk")

    add_card(s2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
             "Manual Shariah Scrubbing", 
             ["Shariah teams must manually comb line-by-line through 'Other Income' footnotes.",
              "Conventional deposit interest income requires legally binding Taharah purification.",
              "Manual Zakat and purification math creates governance friction before drawdown."],
             border_color=c_blue, accent_sub="Governance Delay")

    # ==================== SLIDE 3: THE SOLUTION ====================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3)
    add_header(s3, "SANAD Architecture: Autonomous Forensic Intelligence")

    add_card(s3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "1. Forensic Circularization",
             ["Multi-Document Parser: Ingests audited financials, CiNet bureau reports, MOCI registry extracts, and PACI data simultaneously.",
              "Adversarial Discrepancy Hunter: Cross-examines declarations against registry filings to uncover undisclosed liabilities.",
              "Sovereign Redaction: Client PII sanitized in accordance with Central Bank of Kuwait (CBK) sovereign data rules."],
             border_color=c_blue, accent_sub="Zero Document Isolation")

    add_card(s3, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "2. Shariah & Financial Core",
             ["AAOIFI Standard No. 21 Engine: Automatically calculates non-halal income ratio (<5% ceiling) and debt-to-assets ratio (<30% ceiling).",
              "Taharah Cleansing Mandate: Calculates exact dividend purification down to the fil and drafts Bait Al-Zakat remittance transfer order.",
              "Covenant Stress Simulator: Monte Carlo stress testing under -25% revenue downturns and +150 bps discount rate hikes."],
             border_color=c_emerald, accent_sub="Automated Compliance")

    # ==================== SLIDE 4: TRACK 1 DELIVERABLE ====================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4)
    add_header(s4, "Track 1 Deliverable: Client Documentation Studio")

    add_card(s4, Inches(0.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "Credit Memo (CAM)",
             ["Warba Bank official executive memorandum format.",
              "Comprehensive borrower appraisal, revenue velocity, and debt coverage.",
              "Verbatim page citations with SHA-256 grounding hashes."],
             border_color=c_blue, accent_sub="Official Banking Template")

    add_card(s4, Inches(3.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "Murabaha Term Sheet",
             ["Binding facility structure (Commodity Murabaha / Tawarruq).",
              "Automated margin pricing: CBK Discount Rate + 2.25% p.a.",
              "Covenants: Min 1.25x DSCR & registered first-degree lien."],
             border_color=c_emerald, accent_sub="Financing Agreement")

    add_card(s4, Inches(6.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "RM Executive Brief",
             ["1-page relationship manager cheat-sheet.",
              "Talking points on client strengths, working capital cycle, and expansion.",
              "Up-sell triggers: KWD 700k expansion & LC trade finance."],
             border_color=c_amber, accent_sub="Front-Office Enabler")

    add_card(s4, Inches(9.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "SSB Taharah Memo",
             ["Shariah Supervisory Board endorsement packet.",
              "AAOIFI Standards 21 & 35 compliance certificate.",
              "Pre-drafted Bait Al-Zakat donation voucher prior to drawdown."],
             border_color=RGBColor(168, 85, 247), accent_sub="Shariah Endorsement")

    # ==================== SLIDE 5: CASE STUDY ====================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5)
    add_header(s5, "Forensic Case Study: Gulf Pearl Foods (CR #204918-KW)")

    add_card(s5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "The Deception: Undisclosed Performance Bond",
             ["The Borrower Claim: In Credit Application Clause 5.2, company declared 'Zero Contingent Liabilities & Zero Affiliate Guarantees'.",
              "The Forensic Discovery: SANAD's automated circularization scanned Ministry of Justice Gazette Vol 44 and uncovered an active KWD 350,000 corporate bond issued to sister entity Pearl Logistics.",
              "The Legal Risk: In a corporate liquidation, this undisclosed guarantee would dilute Warba Bank's ranking as senior secured creditor."],
             border_color=RGBColor(239, 68, 68), accent_sub="Discrepancy Ref #F-922")

    add_card(s5, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "The Automated Remediation: Protective Covenant",
             ["Condition Precedent: SANAD automatically synthesized a mandatory Condition Precedent for the credit agreement:",
              "'Borrower must execute an irrevocable Priority & Subordination Deed ranking Warba Bank facility senior to affiliate guarantee.'",
              "Audited Citations: Directly links credit committee members to Gazette Entry 18 and Balance Sheet Note 14 in 1 click.",
              "Result: Prevents KWD 350,000 credit impairment before facility drawdown."],
             border_color=c_emerald, accent_sub="Autonomous Legal Armor")

    # ==================== SLIDE 6: SHARIAH TAHARAH ====================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6)
    add_header(s6, "Shariah Governance: AAOIFI Standard No. 21 & Taharah")

    add_card(s6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Non-Halal Revenue Purification",
             ["Footnote Forensic Screening: Screened P&L Note 7 ('Other Income') and detected KWD 7,900 in conventional deposit interest.",
              "AAOIFI Standard 21 Compliance: Prohibited income stands at 0.09% of turnover, safely below the 5.0% maximum ceiling.",
              "Mandatory Disgorgement: 100% of the KWD 7,900 must be disgorged to designated charity Bait Al-Zakat Kuwait before facility disbursement."],
             border_color=c_emerald, accent_sub="AAOIFI Standard No. 21")

    add_card(s6, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Zakat Base Computation",
             ["Step-Down Zakat Calculation: Zakatable base proxy computed at KWD 3,480,000 (60% of total assets).",
              "Solar Calendar Rate: Applied 2.577% solar Zakat factor (AAOIFI Standard No. 35) = KWD 89,679 payable.",
              "Ready Transfer Order: Pre-drafts electronic remittance voucher so relationship manager can close the transaction without Shariah audit delays."],
             border_color=c_blue, accent_sub="AAOIFI Standard No. 35")

    # ==================== SLIDE 7: BUSINESS IMPACT ====================
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7)
    add_header(s7, "Proactive RM Radar & Commercial Impact")

    add_card(s7, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Turnaround Velocity",
             ["11 Days → 38 Seconds",
              "94% reduction in manual document synthesis time.",
              "Accelerates credit approval turnaround from 2 weeks to same-day committee review.",
              "Allows Warba Bank to win prime commercial borrowers first."],
             border_color=c_blue, accent_sub="Time-to-Yes")

    add_card(s7, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Proactive Balance-Sheet Growth",
             ["+KWD 700K Facility Expansion",
              "Identified unencumbered liquid inventory cushion of KWD 1.2M.",
              "Automatically recommended +KWD 700k Murabaha facility expansion.",
              "Generates +KWD 39,375 annual net profit margin for Warba Bank."],
             border_color=c_emerald, accent_sub="RM Revenue Radar")

    add_card(s7, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Zero Compromise Governance",
             ["Cryptographic Proof Ledger",
              "Every footnote bound to SHA-256 hash and Merkle root block height.",
              "Sequential 3-tier digital sign-offs (Analyst, SCU, Credit Committee).",
              "Complete compliance with CBK circulars and AAOIFI standards."],
             border_color=c_amber, accent_sub="Institutional Audit")

    # ==================== SLIDE 8: SUMMARY & DEMO ====================
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8)
    add_header(s8, "Ready for Production: Live Demo & Verification")

    add_card(s8, Inches(0.8), Inches(1.8), Inches(11.6), Inches(4.8),
             "Test the Live Production Application Directly",
             [
               "🌐 Live Production Web App: https://sanad-engine.netlify.app",
               "⚡ Live Backend API: https://sanad-production-9d51.up.railway.app",
               "📂 GitHub Code Repository: https://github.com/anajimdeen01-debug/sanad-frontend",
               " ",
               "HOW TO EVALUATE IN 60 SECONDS:",
               "1. Open Gulf Pearl Foods Trading (CR #204918-KW) from the main directory.",
               "2. Read the 4 AI Forensic Chapters authored dynamically by Google Gemini.",
               "3. Click citation [#F-922: Undisclosed Bond] to inspect the document provenance modal.",
               "4. Click '⚡ Re-Analyze with Gemini' to watch live unscripted reasoning in real-time.",
               "5. Slide the Revenue Stress slider to -25% and observe real-time DSCR recalculation.",
               "6. Switch to 'Client Documentation Studio' to inspect the CAM, Term Sheet, and RM Brief."
             ],
             border_color=c_emerald, accent_sub="Self-Guided Evaluation Protocol")

    prs.save(output_path)
    print(f"Presentation saved to: {output_path}")

if __name__ == '__main__':
    out_dir = r"c:\Users\DELL-PC\sanad-v2\submission"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "SANAD_Pitch_Deck_Warba_Bank.pptx")
    create_deck(out_file)
