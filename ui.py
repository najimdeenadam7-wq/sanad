import hashlib, json, os, re, time
from pathlib import Path
import streamlit as st
import ingest, retrieve, generate, shariah, gaps, structure, branding, parsers, governance
from generate import CIT

DATA = Path("data")
st.set_page_config(page_title="Sanad v3.5 — Warba Bank", layout="wide", page_icon="🕌")

branding.inject()
branding.header()

if not (DATA/"clients.json").exists():
    import subprocess, sys
    subprocess.run([sys.executable, "make_synthetic_data.py"], check=True)

# ---------------- AUTH GATE (config-flagged: open for judges, locked for pilot) ----------------
AUTH_ON = bool(os.environ.get("SANAD_AUTH_ENABLED"))
if AUTH_ON:
    if "role" not in st.session_state:
        st.title("🔐 Sanad — Sign in")
        role = st.selectbox("Role", governance.ROLES)
        pw = st.text_input("Password", type="password")
        if st.button("Sign in", key="login_btn"):
            if pw == governance.DEMO_USERS[role]:
                st.session_state.role = role
                governance.log_event(role, "login", "-")
                st.rerun()
            else:
                st.error("Invalid credentials")
        st.stop()
    user = st.session_state.role
else:
    user = st.session_state.get("role", "demo")
    st.caption("Demo mode: authentication disabled. Set SANAD_AUTH_ENABLED=1 in the hosting environment "
               "to activate role-based access (rm / credit / scu). Production: SSO/RBAC per Warba IT policy.")

BADGE = {"HIGH":"🔴 HIGH","MEDIUM":"🟡 MEDIUM","PRESENT":"🟢 Present","EXPIRED":"🟡 Expired","MISSING":"🔴 Missing"}

def fmt(v):
    if v is None: return "—"
    return f"{v:,.1f}" if isinstance(v, float) else f"{v:,.0f}"

def md_table(headers, rows):
    t = "| " + " | ".join(headers) + " |\n|" + "|".join(["---"]*len(headers)) + "|\n"
    return t + "".join("| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in r) + " |\n" for r in rows)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Control Panel")
    st.markdown(f"**Signed in as:** `{user}`")
    clients = json.loads((DATA/"clients.json").read_text())
    cid = st.selectbox("Client", list(clients), format_func=lambda c: clients[c]["name"])
    st.markdown(f"**Sector:** {clients[cid]['sector']}")
    st.divider()
    use_llm = st.checkbox("LLM prose mode", True,
                          help="Uses ANTHROPIC_API_KEY or OPENAI_API_KEY (NVIDIA/Groq/Ollama). Falls back to extractive if none.")
    baseline = st.number_input("Manual baseline (hours)", 1.0, 60.0, 20.0)

    st.divider()
    st.markdown("#### 📎 Upload sources")
    up_kind = st.selectbox("Treat uploads as", ["internal", "external"], key="up_kind")
    ups = st.file_uploader("Documents (pdf, docx, csv, txt, md, json)",
                           type=["pdf","docx","csv","txt","md","json"],
                           accept_multiple_files=True, key="upl")
    uploads_changed = False
    processed = st.session_state.setdefault("processed_uploads", set())
    if ups:
        for up in ups:
            sig = (cid, up.name, up.size)
            if sig in processed: continue
            try:
                text = parsers.parse_uploaded(up.name, up.getvalue())
            except Exception as e:
                st.warning(f"Skipped {up.name}: {e}")
                processed.add(sig)
                continue
            safe = re.sub(r"[^a-z0-9]+", "_", up.name.lower()).strip("_")
            prefix = "ext_" if up_kind == "external" else "int_"
            (DATA/cid/f"{prefix}up_{safe}.md").write_text(text, encoding="utf-8")
            processed.add(sig)
            uploads_changed = True
            governance.log_event(user, "upload", cid, f"{up.name} as {up_kind}")
            st.success(f"Added {up.name} as {up_kind} source.")
    existing = sorted(p.name for p in (DATA/cid).glob("*_up_*.md"))
    if existing:
        st.caption("Uploaded into this file: " + ", ".join(existing))
        if st.button("🗑 Remove uploaded sources", key="clr_up"):
            for p in (DATA/cid).glob("*_up_*.md"): p.unlink()
            st.session_state["processed_uploads"] = set()
            st.session_state.pop("res", None)
            governance.log_event(user, "remove_uploads", cid)
            st.rerun()
    st.divider()
    st.markdown("**Pipeline**\n\n1️⃣ Ingest → 2️⃣ Retrieve → 3️⃣ Generate → 4️⃣ Screen → 5️⃣ Govern")

# ---------------- ASSEMBLE ----------------
assemble_clicked = st.button("⚡ Assemble / Refresh Client File", type="primary",
                             use_container_width=True, key="assemble_btn")

need = (("res" not in st.session_state) or assemble_clicked or uploads_changed
        or (st.session_state.get("cid") != cid))

if need:
    try:
        t0 = time.perf_counter()
        with st.spinner("Assembling client file…"):
            sources = ingest.load_client(DATA/cid)
            chunks = ingest.all_chunks(sources)
            bm = retrieve.BM25(chunks)
            memo = generate.assemble(clients[cid], chunks, bm, use_llm)
            fin_raw = json.loads((DATA/cid/"financials.json").read_text())
            screen = shariah.screen(fin_raw, chunks)
            gp = gaps.detect(json.loads((DATA/cid/"kyc_status.json").read_text()), clients[cid]["name"])
            elapsed = time.perf_counter() - t0
        st.success(f"Assembled in {elapsed:.2f}s")
        governance.log_event(user, "assemble", cid, f"{elapsed:.2f}s, {len(memo['citations'])} citations")
        st.session_state.res = dict(memo=memo, screen=screen, gaps=gp, elapsed=elapsed,
                                    chunks=chunks, cmap={},
                                    struct=structure.load(DATA/cid, clients[cid]))
        st.session_state.cid = cid
    except Exception as e:
        st.error(f"Assembly failed: {e}")
        st.stop()

# ---------------- SHARED STATE ----------------
r = st.session_state.res
S = r["struct"]
saved = baseline - r["elapsed"] / 3600

def ren(text):
    return CIT.sub(lambda m: f"[{r['cmap'].setdefault(m.group(1), len(r['cmap'])+1)}]", text)

rendered_sections = {s["id"]: ren(s["text"]) for s in r["memo"]["sections"]}

FIN = {k: (v24, v25) for k, v24, v25 in S["metrics"]}
debt = FIN["Interest-bearing Debt (KWD)"][1] or 0
ng = len([x for x in S['docs'] if x[1] != 'PRESENT'])

# ---------------- KPI STRIP ----------------
k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Shariah Score", f"{r['screen']['score']}/100")
k2.metric("Open Gaps", ng)
k3.metric("Assembly Time", f"{r['elapsed']:.2f}s")
k4.metric("Hours Returned", f"{saved:.1f}h")
k5.metric("Citations", len(r["memo"]["citations"]))
st.divider()

# ---------------- TABS ----------------
t_file,t_fin,t_sh,t_zk,t_gp,t_br,t_ar,t_im,t_ex = st.tabs(
    ["📋 Credit File","💰 Financials","🕌 Shariah & Restructuring","🌙 Zakat",
     "📎 Gaps & Outreach","📱 RM Briefing","🌐 ملخص عربي","📈 Impact","✅ Approve & Export"])

with t_file:
    a,b = st.columns(2)
    with a.container(border=True):
        st.markdown("#### 🏢 Client Profile")
        st.markdown(md_table(["Field","Value"], list(S["profile"].items())))
    with b.container(border=True):
        st.markdown("#### 🕑 Relationship Timeline")
        st.markdown(md_table(["Date","Source","Event"], S["timeline"]))
    a,b = st.columns(2)
    with a.container(border=True):
        st.markdown("#### 👥 Shareholders (Registry)")
        if S["shareholders"]:
            st.markdown(md_table(["Party","Stake"], S["shareholders"]))
        else:
            st.caption("No shareholder data.")
        for note in S["registry_notes"]:
            st.warning(note)
    with b.container(border=True):
        st.markdown("#### 📰 External News Signals")
        st.markdown(md_table(["Date","Headline"], S["news"]))
    with st.expander(f"🔍 Citation appendix ({len(r['cmap'])} sources cited in memo)"):
        rows = []
        for c_id, n in sorted(r["cmap"].items(), key=lambda kv: kv[1]):
            ch = next((x for x in r["chunks"] if x.chunk_id == c_id), None)
            rows.append((n, c_id,
                         ch.doc if ch else "—",
                         ch.kind if ch else "—",
                         governance.CONSENT_BASIS.get(ch.kind, "—") if ch else "—",
                         (ch.text[:110] + "…") if ch else "—"))
        st.markdown(md_table(["#","Citation ID","Document","Type","Data basis","Excerpt"], rows))

with t_fin:
    rev24, rev25 = FIN["Revenue (KWD)"]
    ni24, ni25 = FIN["Net Income (KWD)"]
    c1,c2,c3 = st.columns(3)
    c1.metric("Revenue FY25", fmt(rev25),
              delta=f"{((rev25-rev24)/rev24)*100:+.1f}%" if (rev24 and rev25) else None)
    c2.metric("Net Income FY25", fmt(ni25),
              delta=f"{((ni25-ni24)/ni24)*100:+.1f}%" if (ni24 and ni25) else None)
    c3.metric("Gross Margin", f"{fmt(FIN['Gross Margin (%)'][1])}%")
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Assets", fmt(FIN["Total Assets (KWD)"][1]))
    c2.metric("Total Equity", fmt(FIN["Total Equity (KWD)"][1]))
    c3.metric("Interest-bearing Debt", fmt(debt),
              delta="conventional exposure" if debt else None, delta_color="inverse")
    st.markdown("#### Year-over-Year Comparison")
    st.markdown(md_table(["Metric","FY2024","FY2025","Change"],
        [(k, fmt(v24), fmt(v25), f"{((v25-v24)/v24)*100:+.1f}%" if (v24 and v25) else "—")
         for k, v24, v25 in S["metrics"]]))

with t_sh:
    a,b = st.columns([1,2])
    with a.container(border=True):
        st.metric("Compliance Score", f"{r['screen']['score']}/100")
        st.progress(r["screen"]["score"]/100)
    with b:
        if r["screen"]["flags"]:
            st.markdown(md_table(["Severity","Rule","Finding","Evidence"],
                [(BADGE[f['severity']], f['rule'], f['finding'], f"`{f['evidence']}`")
                 for f in r["screen"]["flags"]]))
            for f in r["screen"]["flags"]:
                st.info(f"➡️ **{f['rule']}** — {f['recommendation']}")
        else:
            st.success("✅ No Shariah flags detected.")
    st.markdown("#### 💡 Conventional → Islamic Restructuring Map")
    if debt:
        st.markdown(md_table(
            ["Conventional Exposure","Shariah Issue","Proposed Islamic Structure","Mechanism","Reference"],
            [["Interest-bearing term debt","Riba (interest accrual)","Murabaha / Sukuk programme",
              "Asset-backed cost-plus sale / investment certificate","AAOIFI SS 8 (Murabaha) / SS 17 (Sukuk)"],
             ["Interest income on idle cash","Riba income","Purification + Islamic deposit",
              "Charitable disposal of interest; migrate cash to Wakala deposit",
              "AAOIFI Shari'ah Standard on Wakala (as adopted by SCU)"]]))
    else:
        st.success("No conventional exposure to restructure.")
    st.markdown("#### 🧾 Shariah Control Unit review queue")
    if r["screen"]["flags"]:
        review = governance.load_review(cid)
        locked = AUTH_ON and user != "scu"
        for f in r["screen"]["flags"]:
            cur = review.get(f["rule"], {})
            cx, cy = st.columns([1,2])
            status = cx.selectbox(f"SCU decision — {f['rule']}", ["pending","approved","rejected"],
                                  index=["pending","approved","rejected"].index(cur.get("status","pending")),
                                  key=f"scu_{f['rule']}", disabled=locked)
            note = cy.text_input("Reviewer note", cur.get("note",""), key=f"scun_{f['rule']}", disabled=locked)
            review[f["rule"]] = dict(status=status, note=note, reviewer=user,
                                     ts=time.strftime("%Y-%m-%d %H:%M"))
        if locked:
            st.caption("Only the `scu` role can record decisions (sign in as scu to edit).")
        if st.button("💾 Save SCU decisions", key="save_scu"):
            governance.save_review(cid, review)
            governance.log_event(user, "scu_review", cid, f"{len(review)} decision(s)")
            st.success("Saved to client file.")
    else:
        st.caption("No flags requiring SCU opinion.")

with t_zk:
    z = shariah.zakat_estimate(S["fin"])
    za = z["zakatable_assets"]; stl = z["short_term_liabilities"]
    base = z["net_base"]; due = z["zakat_due"]
    st.markdown(md_table(["Step","Item","Amount (KWD)"],
        [["1","Zakatable assets (60% of total assets)", fmt(za)],
         ["2","Less: short-term liabilities", f"({fmt(stl)})"],
         ["3","**Net Zakat base**", f"**{fmt(base)}**"],
         ["4","Zakat due @ 2.5%", f"**{fmt(due)}**"]]))
    st.caption("Methodology: simplified net-invested-funds proxy (60% zakatable assets). "
               "Final basis subject to Warba Shariah Control Unit methodology.")
    st.info("💡 **RM talking point:** offer Zakat settlement via Warba's charity channels + purification of doubtful income.")

with t_gp:
    st.markdown(md_table(["Required Document","Status"], [(doc, BADGE[s]) for doc, s in S["docs"]]))
    st.markdown("#### 📧 Auto-drafted outreach email")
    st.code(r["gaps"]["email"])

with t_br:
    risks = []
    if r["screen"]["score"] < 100: risks.append("Shariah flags")
    if ng: risks.append(f"{ng} missing/expired docs")
    txt = (f"🏢 *{clients[cid]['name']}*\n📝 *Ask:* facility review / limit increase\n"
           f"⚠️ *Risk:* {', '.join(risks) if risks else 'low'}\n"
           f"⏱️ *Sanad saved:* {saved:.1f}h\n_Generated by Sanad AI_")
    a,b = st.columns(2)
    a.markdown(f"<div class='wa'>{txt.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
    b.text_area("Copy-ready text", txt, height=160, key="brief_txt")

with t_ar:
    st.markdown("#### 🌐 الملخص التنفيذي بالعربية")
    txt_ar = (f"🏢 *{clients[cid]['name']}*\n"
              f"📝 *الطلب:* مراجعة وتزيادة التسهيلات الائتمانية\n"
              f"🕌 *درجة الامتثال الشرعي:* {r['screen']['score']}/100\n"
              f"📋 *المستندات الناقصة أو المنتهية:* {ng}\n"
              f"⏱️ *الوقت الموفَّر عبر محرك سند:* {saved:.1f} ساعة\n"
              "_أُنشئ تلقائيًا بواسطة محرك سند — النسخة التجريبية_")
    st.markdown(f"<div class='wa'>{txt_ar.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
    st.caption("Pilot phase: full Arabic memo prose via Warba-approved private LLM endpoint.")

with t_im:
    st.markdown(md_table(["Workflow Step","Manual (hours)","Sanad (seconds)"],
        [["Source gathering","4.0","1.2"],["Financial analysis","6.0","0.8"],
         ["Memo drafting","7.0","1.5"],["Shariah & compliance check","2.5","0.5"],
         ["Gap follow-up emails","0.5","0.2"],
         ["**Total**", f"**{baseline:.1f}**", f"**{r['elapsed']:.1f}**"]]))
    c1,c2 = st.columns(2)
    c1.metric("Hours returned per deal", f"{saved:.1f}")
    c2.metric("Annualised (40 deals / RM)", f"{saved*40:.0f}h")
    st.progress(min(1.0, saved / baseline))

with t_ex:
    edits = {}
    for s in r["memo"]["sections"]:
        with st.expander(s["title"]):
            edits[s["id"]] = st.text_area("Narrative", rendered_sections[s["id"]], height=120,
                                          key=f"e_{s['id']}", label_visibility="collapsed")
    st.markdown("#### 🖋 Approval chain")
    approvals = {}
    for role_label in ["RM", "Credit", "Shariah Control Unit"]:
        approvals[role_label] = st.checkbox(f"{role_label} approval", key=f"appr_{role_label}")
        if approvals[role_label]:
            governance.log_event(user, "approve", cid, role_label)
    st.markdown(md_table(["Approver","Status"],
        [(k, "✅ Approved" if v else "⏳ Pending") for k, v in approvals.items()]))

    md = f"# Credit Memorandum — {clients[cid]['name']}\n_Generated by Sanad v3.5_\n\n"
    md += "## Client Profile\n" + md_table(["Field","Value"], list(S["profile"].items())) + "\n"
    md += "## Financial Summary\n" + md_table(["Metric","FY2024","FY2025","Change"],
          [(k, fmt(v24), fmt(v25), f"{((v25-v24)/v24)*100:+.1f}%" if (v24 and v25) else "—")
           for k, v24, v25 in S["metrics"]]) + "\n"
    for s in r["memo"]["sections"]:
        md += f"## {s['title']}\n{edits[s['id']]}\n\n"
    md += "## Approvals\n" + md_table(["Approver","Status"],
          [(k, "Approved" if v else "Pending") for k, v in approvals.items()]) + "\n"
    md += ("## Client-Facing Summary\nIn plain terms: your relationship team has prepared an updated "
           f"credit file for {clients[cid]['name']}. Outstanding items: {ng if ng else 'none'}. "
           "Warba Bank will contact you for any required documents.\n"
           f"بالعربية: قام فريق إدارة العلاقة بتحديث الملف الائتماني لشركة {clients[cid]['name']}؛ "
           "سيتم التواصل بشأن أي مستندات مطلوبة.\n\n")
    md += "## Citation Appendix\n"
    for c_id, n in sorted(r["cmap"].items(), key=lambda kv: kv[1]):
        md += f"{n}. `{c_id}`\n"
    ver = hashlib.sha256(md.encode()).hexdigest()[:12]
    seen = st.session_state.setdefault("export_versions", set())
    if ver not in seen:
        seen.add(ver)
        governance.log_event(user, "export_version", cid, ver)
    st.caption(f"Document version: `{ver}` (hash-logged in audit trail)")
    st.download_button("⬇️ Download memo (.md)", md,
                       file_name=f"sanad_memo_{cid}_{ver}.md", use_container_width=True, key="dl_memo")
    with st.expander("🕵️ Audit trail (tamper-evident, hash-chained)"):
        st.markdown(md_table(["Time","User","Action","Client","Detail","Hash"],
            [(e.get("ts"), e.get("user"), e.get("action"), e.get("client"),
              e.get("detail"), f"`{e.get('hash')}`") for e in governance.read_audit(20)]))

branding.footer()