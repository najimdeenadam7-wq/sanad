// wire.js - Unified client file engine script
const BASE_API = window.API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:8000' : '');

// Auth guard & global fetch wrapper
(function() {
  const token = localStorage.getItem('token') || localStorage.getItem('sanad_token');
  const user = JSON.parse(localStorage.getItem('user') || localStorage.getItem('sanad_user') || 'null');
  
  if (!token && !window.location.pathname.includes('login')) {
    window.location.href = '/login';
    return;
  }

  // Inject user badge into topbar
  const actions = document.querySelector('.top-actions');
  if (actions && user) {
    const badge = document.createElement('span');
    badge.style.cssText = 'font-family:var(--mono);font-size:11px;color:var(--muted);margin-right:12px';
    badge.textContent = `${user.email} · ${user.role || 'Officer'}`;
    actions.insertBefore(badge, actions.firstChild);
    
    const logout = document.createElement('button');
    logout.className = 'btn-ghost btn';
    logout.innerHTML = '<i class="ph-bold ph-sign-out"></i>Sign out';
    logout.onclick = () => {
      localStorage.clear();
      window.location.href = '/login';
    };
    actions.appendChild(logout);
  }

  // Attach token to all outgoing fetch requests
  const originalFetch = window.fetch;
  window.fetch = async function(url, opts = {}) {
    opts.headers = opts.headers || {};
    const curToken = localStorage.getItem('token') || localStorage.getItem('sanad_token');
    if (curToken && typeof opts.headers === 'object' && !opts.headers['Authorization']) {
      opts.headers['Authorization'] = 'Bearer ' + curToken;
    }
    try {
      const resp = await originalFetch(url, opts);
      if (resp.status === 401 && !window.location.pathname.includes('login')) {
        localStorage.clear();
        window.location.href = '/login';
      }
      return resp;
    } catch (err) {
      console.error("Network error:", err);
      throw err;
    }
  };
})();

/* Sanad wire layer — replaces every hardcoded number with live engine data. */
const $ = (s, r=document) => r.querySelector(s);
const $$ = (s, r=document) => [...r.querySelectorAll(s)];
const fmtC = (v, d=0) => Number(v).toLocaleString('en-US', {minimumFractionDigits:d, maximumFractionDigits:d});
const BASELINE = 20.0;
const state = { client:null, use_llm:true };

let toastH;
function toast(m){ const t=$('#toast'); if(!t) return; t.textContent=m; t.classList.add('show');
  clearTimeout(toastH); toastH=setTimeout(()=>t.classList.remove('show'), 2600); }
const badge = sev => `<span class="tag ${sev==='HIGH'?'red':sev==='MEDIUM'?'yellow':'green'}">${sev}</span>`;
const status = (ok,label) => `<span class="status ${ok?'ok':'bad'}"><span class="d"></span>${label}</span>`;
const tbody = (panel, i) => { const t = $$(panel+' table')[i]; return t ? t.querySelector('tbody') : null; };
const setRows = (tb, html) => { if(tb) tb.innerHTML = html; };

async function load(){
  if(!state.client) return;
  const res = await fetch('/api/assemble', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({client: state.client, use_llm: state.use_llm})});
  render(await res.json());
}

function render(p){
  if(!p.sources){
    $('.kicker').innerHTML = `<span class="dot"></span>Empty file — upload sources to begin`;
    $('#assembleStatus').textContent = 'No sources yet';
  }
  const saved = BASELINE - p.elapsed/3600;
  $('.kicker').innerHTML = `<span class="dot"></span>Client file · Assembled in ${p.elapsed}s · ${p.citations.length} citations verified · mode ${p.mode}`;
  $('h1').textContent = p.name;
  $('.lede').innerHTML = `${p.sector}. <strong>${p.profile['CR No.']||'—'}</strong>, ${p.profile['Registered Capital']||'—'}. Relationship manager <strong>${p.profile['Relationship Manager']||'—'}</strong>. Request: facility review / limit increase.`;
  $('.meta-row').innerHTML = [
    `Sector · <b>${p.sector}</b>`,
    `Registry · <b>${p.profile['Registry Status']||'—'} to ${p.profile['Valid Until']||'—'}</b>`,
    `Signatories · <b>${(p.profile['Signatories']||'—').split(';')[0]}</b>`,
    `Baseline · <b>${BASELINE.toFixed(1)}h manual</b>`].map(t=>`<span class="meta-chip">${t}</span>`).join('');

  const cs = $$('.bento [data-count]');
  const set = (el,v,d=0,comma=false)=>{ if(!el) return; el.textContent = comma?fmtC(v,d):Number(v).toFixed(d); };
  set(cs[0], p.score); set(cs[1], p.gaps.length); set(cs[2], p.elapsed, 2); set(cs[3], saved, 1); set(cs[4], p.citations.length);
  $$('.score-bar i').forEach(b => b.style.width = p.score + '%');
  $('#assembleStatus').textContent = `Assembled in ${p.elapsed}s — ${p.citations.length} citations resolved`;

  setRows(tbody('#p-credit',0), Object.entries(p.profile).map(([k,v])=>`<tr><td>${k}</td><td>${v}</td></tr>`).join(''));
  setRows(tbody('#p-credit',1), p.timeline.map(([d,s,e])=>`<tr><td class="mono">${d}</td><td><span class="tag blue">${s}</span></td><td>${e}</td></tr>`).join(''));
  setRows(tbody('#p-credit',2), p.shareholders.map(([a,b])=>`<tr><td>${a}</td><td class="num">${b}</td></tr>`).join(''));
  setRows(tbody('#p-credit',3), p.news.map(([d,h])=>`<tr><td class="mono">${d}</td><td>${h}</td></tr>`).join(''));
  const cc = $('#p-credit .callout'); if(cc) cc.innerHTML = `<span class="who">Citation appendix</span>${p.citations.length} sources cited · every claim carries a receipt (${p.citations.map(c=>c.id).slice(0,3).join(', ')}…).`;

  const fc = $$('#p-financials .bento [data-count]');
  const fin = p.metrics; const gv = k => (fin.find(m=>m[0]===k)||[null,null,null]);
  const [,r24,r25] = gv('Revenue (KWD)'); const [,n24,n25] = gv('Net Income (KWD)');
  const [, ,mg] = gv('Gross Margin (%)'); const [, ,ta] = gv('Total Assets (KWD)');
  const [, ,te] = gv('Total Equity (KWD)'); const [, ,db] = gv('Interest-bearing Debt (KWD)');
  set(fc[0], r25, 0, true); set(fc[1], n25, 0, true); set(fc[2], mg, 1); set(fc[3], ta, 0, true); set(fc[4], te, 0, true); set(fc[5], db, 0, true);
  setRows(tbody('#p-financials',0), fin.length ? fin.map(([k,v24,v25])=>{
    const ch = (v24&&v25)? `${((v25-v24)/v24*100)>=0?'+':''}${((v25-v24)/v24*100).toFixed(1)}%` : '—';
    const d = k.includes('(%)')?1:0;
    return `<tr><td>${k}</td><td class="num">${v24==null?'—':fmtC(v24,d)}</td><td class="num">${v25==null?'—':fmtC(v25,d)}</td><td class="num">${ch}</td></tr>`;
  }).join('') : `<tr><td colspan="4" class="mono">No financial statements uploaded yet.</td></tr>`);

  setRows(tbody('#p-shariah',0), p.flags.length
    ? p.flags.map(f=>`<tr><td>${badge(f.severity)}</td><td>${f.rule}</td><td>${f.finding}</td><td><span class="cite">${f.evidence}</span></td></tr>`).join('')
    : `<tr><td colspan="4">${status(true,'No flags — file clean')}</td></tr>`);
  const sTag=$('#scoreTag'); if(sTag) sTag.textContent = p.sources ? `${p.flags.length} flag(s)` : 'awaiting sources';
  const q = $('#scuQueue');
  if(q){
    q.innerHTML = p.flags.map(f=>{ const cur=(p.review||{})[f.rule]||{};
      return `<div class="field" style="display:flex;flex-direction:column;gap:4px;flex:1;min-width:200px">
        <label style="font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)">SCU decision — ${f.rule}</label>
        <select data-rule="${f.rule}" style="font-size:14px;border:1px solid var(--line);border-radius:6px;padding:9px 12px;background:var(--canvas)">
          <option ${cur.status==='pending'?'selected':''}>pending</option><option ${cur.status==='approved'?'selected':''}>approved</option><option ${cur.status==='rejected'?'selected':''}>rejected</option>
        </select></div>
        <div class="field" style="display:flex;flex-direction:column;gap:4px;flex:2;min-width:200px">
        <label style="font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)">Reviewer note</label>
        <input data-note="${f.rule}" value="${cur.note||''}" placeholder="Basis for decision…" style="font-size:14px;border:1px solid var(--line);border-radius:6px;padding:9px 12px"></div>`;
    }).join('') + (p.flags.length ? `<button class="btn" id="scuSave" type="button">Save SCU decisions</button>` : `<span class="m-note">No flags requiring SCU opinion.</span>`);
    const sb = $('#scuSave');
    if(sb) sb.onclick = async () => {
      const dec = {};
      $$('#scuQueue select').forEach(s=>{ const rule=s.dataset.rule;
        const note = $(`#scuQueue input[data-note="${rule}"]`); dec[rule] = {status:s.value, note:note?note.value:''}; });
      await fetch('/api/scu',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({client:state.client, decisions:dec})});
      toast('SCU decisions recorded in audit trail'); load();
    };
  }

  const z = p.zakat;
  setRows(tbody('#p-zakat',0), z ? [
    `<tr><td class="mono">1</td><td>Zakatable assets (60% of total assets)</td><td class="num">${fmtC(z.zakatable_assets,1)}</td></tr>`,
    `<tr><td class="mono">2</td><td>Less: short-term liabilities</td><td class="num">(${fmtC(z.short_term_liabilities)})</td></tr>`,
    `<tr><td class="mono">3</td><td>Net Zakat base</td><td class="num">${fmtC(z.net_base,1)}</td></tr>`,
    `<tr><td class="mono">4</td><td>Zakat due @ 2.5%</td><td class="num"><strong>${fmtC(z.zakat_due,1)}</strong></td></tr>`].join('')
    : `<tr><td colspan="3" class="mono">No audited financials yet — upload statements to compute Zakat.</td></tr>`);

  setRows(tbody('#p-gaps',0), (p.docs || p.gaps.map(g=>[g.doc,g.status])).map(([d,s])=>`<tr><td>${d}</td><td>${(s==='PRESENT'||s==='DETECTED')?status(true,s==='DETECTED'?'Detected':'Present'):status(false,s)}</td></tr>`).join(''));
  const em = $('#p-gaps .email'); if(em) em.textContent = p.email;

  const risks = []; if(p.score<100) risks.push('Shariah flags'); if(p.gaps.length) risks.push(`${p.gaps.length} missing/expired docs`);
  const brief = `${p.name} — Ask: facility review / limit increase. Risk: ${risks.length?risks.join(', '):'low'}. Sanad saved ${saved.toFixed(1)}h. Generated by Sanad AI.`;
  const bc = $('#briefCallout'); if(bc) bc.textContent = brief;
  const be = $('#briefEmail'); if(be) be.textContent = brief;
  const ar = $('#arBody'); if(ar) ar.textContent = `${p.name} · درجة الالتزام الشرعي ${p.score}/100 · مستندات ناقصة أو منتهية: ${p.gaps.length} · الوقت الموفّر ${saved.toFixed(1)} ساعة · ${p.citations.length} شاهداً موثقاً.`;

  const ic = $$('#p-impact [data-count]'); set(ic[0], saved, 1); set(ic[1], saved*40, 0, true);
}

/* events */
async function refreshClients(keep){
  const list = await (await fetch('/api/clients')).json();
  const sel = $('#clientSelect');
  sel.innerHTML = Object.entries(list).map(([cid,c])=>`<option value="${cid}">${c.name}</option>`).join('')
    || '<option value="">— no client files yet —</option>';
  if(keep && [...sel.options].some(o=>o.value===keep)) sel.value = keep;
  state.client = sel.value || null;
  return Object.keys(list).length;
}
function injectBootstrap(){
  if($('#bootstrapRow')) return;
  const row = document.createElement('div');
  row.id = 'bootstrapRow'; row.className = 'field'; row.style.flex = '1 1 100%';
  row.innerHTML = `<label>Start a new client file (or load the demo cast)</label>
  <div style="display:flex;gap:8px;flex-wrap:wrap">
  <input id="ncName" placeholder="Company name (e.g. YourCo Holdings K.S.C.)">
  <input id="ncSector" placeholder="Sector">
  <input id="ncCR" placeholder="CR No. (optional)">
  <button class="btn" id="ncCreate" type="button"><i class="ph-bold ph-plus"></i>Create file</button>
  <button class="btn btn-ghost" id="ncSamples" type="button"><i class="ph-bold ph-download"></i>Load sample portfolio</button>
  </div>`;
  document.querySelector('.control').prepend(row);
  $('#ncCreate').onclick = async () => {
    const name = $('#ncName').value.trim(); if(!name){toast('Company name required');return}
    const r = await fetch('/api/clients',{method:'POST',headers:{'Content-Type':'application/json'},
      body: JSON.stringify({name, sector: $('#ncSector').value.trim(), cr: $('#ncCR').value.trim()})});
    const {cid} = await r.json();
    toast('Client file created — upload sources to begin');
    await refreshClients(cid); load();
  };
  $('#ncSamples').onclick = async () => {
    await fetch('/api/samples',{method:'POST'});
    toast('Sample portfolio loaded (4 synthetic clients)');
    await refreshClients(); load();
  };
}
document.addEventListener('DOMContentLoaded', async () => {
  const sel = $('#clientSelect');
  sel.onchange = () => { state.client = sel.value; if(state.client) load(); };
  $('#kindSelect').onchange = () => {};
  $('#assembleBtn').onclick = () => load();
  $('#fileInput').onchange = async e => {
    if (!e.target.files.length) return;
    toast('Ingesting & auto-extracting borrower info...');
    const fd = new FormData();
    if (state.client) fd.append('client', state.client);
    fd.append('kind', $('#kindSelect').value.toLowerCase());
    for (const f of e.target.files) fd.append('files', f);
    
    try {
      const res = await fetch('/api/upload', { method: 'POST', body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Upload failed');
      
      toast('Document(s) ingested & borrower profile created!');
      if (data.business_id) {
        await refreshClients(data.business_id);
      }
      load();
    } catch (err) {
      toast('Upload error: ' + (err.message || 'Failed'));
    }
  };
  $('#rmUp').onclick = async () => {
    await fetch('/api/remove_uploads',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({client:state.client})});
    toast('Uploaded sources removed'); load();
  };
  $$('[data-tick]').forEach(t => t.addEventListener('click', () => {
    const on = t.classList.contains('on');
    fetch('/api/approve',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({client:state.client, role:t.dataset.role, on})});
  }));
  $('#dlBtn').onclick = () => { window.location = `/api/export?client=${state.client}`; toast('Memo downloaded — export logged in audit trail'); };
  const n = await refreshClients();
  if(n === 0) injectBootstrap();
  if(state.client) load();
});