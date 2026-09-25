"""Sanad brand theme: teal/gold lockup, CSS-drawn logo (no image files needed)."""
import streamlit as st

CSS = """
/* ===== SANAD BRAND THEME ===== */
html, body, [class*="st-"] { font-family: "Segoe UI", Inter, system-ui, sans-serif; }

/* ---- offline-environment fix: Streamlit widget icons are Material Symbols
   ligature text; when the font is blocked the raw words ("arrow_drop_down",
   "check_circle") print OVER labels. Hide them by testid (version-stable),
   then draw our own arrows. ---- */
[data-testid="stIconMaterial"],
span.material-symbols-rounded,
[class*="material-symbols"] {
  font-size:0 !important; line-height:0 !important;
  width:0 !important; height:0 !important;
  overflow:hidden !important; display:inline-block !important;
}
[data-testid="stExpander"] summary::before,
[data-testid="stStatus"] summary::before {content:"▸ "; color:#7FD1D8; font-size:1rem;}
[data-testid="stExpander"] details[open] summary::before,
[data-testid="stStatus"] details[open] summary::before {content:"▾ "; color:#E4C565; font-size:1rem;}

/* brand bar + CSS logo */
.brand-bar {display:flex; align-items:center; gap:14px; padding:6px 2px 14px;
            border-bottom:1px solid rgba(201,162,39,.45); margin-bottom:20px;}
.logo-mark {width:46px;height:46px;border-radius:12px;position:relative;flex:none;
            background:linear-gradient(135deg,#0E7C86,#0A5C63);box-shadow:0 2px 10px rgba(0,0,0,.45);}
.logo-crescent {position:absolute;left:10px;top:10px;width:26px;height:26px;border-radius:50%;
                border:4px solid transparent;border-left:4px solid #C9A227;border-top:4px solid #C9A227;
                transform:rotate(-45deg);}
.logo-lines {position:absolute;right:9px;top:14px;width:16px;height:18px;
             background:linear-gradient(#E6EDF3,#E6EDF3) 0 0/16px 3px,
                        linear-gradient(#E6EDF3,#E6EDF3) 0 7px/16px 3px,
                        linear-gradient(#E6EDF3,#E6EDF3) 0 14px/10px 3px;
             background-repeat:no-repeat;}
.brand-title {font-size:24px;font-weight:800;letter-spacing:5px;color:#E6EDF3;line-height:1.1;}
.brand-ar {color:#E4C565;font-size:20px;letter-spacing:0;margin-left:10px;font-weight:600;}
.brand-sub {font-size:12px;color:#9FB3C8;margin-top:2px;}
.brand-pill {margin-left:auto;font-size:11px;padding:6px 12px;border:1px solid rgba(201,162,39,.55);
             color:#E4C565;border-radius:999px;background:rgba(201,162,39,.08);white-space:nowrap;}
.brand-footer {margin-top:34px;padding-top:12px;border-top:1px solid rgba(201,162,39,.3);
               color:#9FB3C8;font-size:12px;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;}

/* headings */
h3, h4 {color:#7FD1D8;}
h3 {border-bottom:1px solid rgba(201,162,39,.35);padding-bottom:6px;}

/* tables */
table {width:100%;border-collapse:collapse;font-size:.88rem;margin:.4rem 0 1rem 0;}
th {text-align:left;padding:8px 10px;background:rgba(14,124,134,.18);color:#BFE6EA;
    border-bottom:2px solid rgba(14,124,134,.5);}
td {padding:7px 10px;border-bottom:1px solid rgba(230,237,243,.08);vertical-align:top;}
tr:nth-child(even) td {background:rgba(255,255,255,.02);}

/* metric tiles */
[data-testid="stMetric"] {background:rgba(14,124,134,.10);border:1px solid rgba(14,124,134,.35);
                          border-radius:12px;padding:12px 14px;}
[data-testid="stMetricLabel"] {color:#7FD1D8;}
[data-testid="stMetricValue"] {color:#E6EDF3;}
[data-testid="stMetricDelta"] {color:#E4C565;}

/* buttons */
button[kind="primary"] {background:linear-gradient(135deg,#0E7C86,#0A5C63)!important;
                        border:1px solid rgba(201,162,39,.5)!important;color:#fff!important;}
button[kind="primary"]:hover {border-color:#E4C565!important;box-shadow:0 0 0 1px rgba(228,197,101,.4);}

/* tabs */
[data-testid="stTabs"] button[aria-selected="true"] {color:#E4C565!important;
                                                     border-bottom:2px solid #C9A227!important;}

/* cards / expanders / code / sidebar */
[data-testid="stVerticalBlockBorderWrapper"] {border-color:rgba(14,124,134,.4)!important;border-radius:14px;}
[data-testid="stExpander"] details {border-color:rgba(14,124,134,.35);border-radius:12px;}
[data-testid="stExpander"] summary {color:#7FD1D8;}
[data-testid="stCode"] {background:#0B1220;border:1px solid rgba(14,124,134,.35);}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#0B1220,#0E1B2E);}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {color:#E4C565;}

/* whatsapp briefing card */
.wa {background:#dcf8c6;color:#111;padding:14px 16px;border-radius:10px;max-width:420px;
     box-shadow:0 1px 2px rgba(0,0,0,.25);font-family:Helvetica,Arial,sans-serif;font-size:.9rem;}
"""

def inject():
    # CSS must be wrapped in <style> tags or Streamlit prints it as page text
    st.markdown("<style>\n" + CSS + "\n</style>", unsafe_allow_html=True)

def header():
    st.markdown("""
    <div class="brand-bar">
      <div class="logo-mark"><span class="logo-crescent"></span><span class="logo-lines"></span></div>
      <div>
        <div class="brand-title">SANAD <span class="brand-ar">سند</span></div>
        <div class="brand-sub">AI Client File Engine · Warba Bank Corporate Banking AI Challenge · Track 1</div>
      </div>
      <div class="brand-pill">v3.3 · Citation-First · Shariah-Compliant</div>
    </div>""", unsafe_allow_html=True)

def footer():
    st.markdown("""
    <div class="brand-footer">
      <span>Sanad v3.3 — built for the Warba Bank Corporate Banking AI Challenge 2026</span>
      <span>Synthetic data only · Demo environment</span>
    </div>""", unsafe_allow_html=True)