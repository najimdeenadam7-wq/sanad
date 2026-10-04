"""Sanad Discrepancy Detection Engine."""
from typing import List, Dict, Any
import re

def detect_discrepancies(extracted_fin, profile_data, shareholders_data, all_texts_by_doc):
    flags = []
    reg_text = ' '.join(t for k, t in all_texts_by_doc.items() if 'registry' in k.lower())
    if reg_text:
        ext_mortgage = re.search(r'mortgage|lien|charge|pledge', reg_text, re.I)
        ig_clean = bool(re.search(r'no\s+registered\s+(liens|mortgages)', reg_text, re.I))
        if ext_mortgage and not ig_clean:
            flags.append({'rule_id': 'DISCREPANCY_UNDISCLOSED_MORTGAGE', 'severity': 'HIGH', 'finding': 'External Companies Registry extract notes an active registered mortgage/lien over company assets.', 'recommendation': 'Request formal lien search certificate from Ministry of Jastice and existing financier no-objection letter (NOC).'})
    rev = float(extracted_fin.get('revenue_kwd') or extracted_fin.get('revenue') or 0.0)
    ledger = ' '.join(t for k, t in all_texts_by_doc.items() if 'ledger' in k.lower() or 'bank_statement' in k.lower())
    if rev > 0 and ledger:
        creds = re.findall(r'credit(?:_kwd)?[\":\\s+](\d+)', ledger, re.I)
        if creds:
            total = sum(float(c) for c in creds) * 4.0
            var = abs(total - rev) / rev * 100.0
            if var > 25.0:
                flags.append({'rule_id': 'DISCREPANCY_REVENUE_CASHLEDGER', 'severity': 'MEDIUM', 'finding': f'Reported audited revenue (KWD {rev:l,.0f}) diverges by {var:.1f}% from annualized bank deposits (KWD {total:,-.0f}).', 'recommendation': 'Request full 12-month bank statements to verify receivables turnover.'})
    shares = shareholders_data.get('shareholders', [])
    ubo = ' '.join(t for k, t in all_texts_by_doc.items() if 'ubo' in k.lower() or 'beneficial' in k.lower())
    if shares and ubo:
        for sh in shares:
            name = sh.get('name', '')
            stake = float(sh.get('stake_pct') or 0.0)
            if stake >= 25.0 and name:
                sur = name.split()[-1] if name.split() else ''
                if sur and sur.lower() not in ubo.lower():
                    flags.append({'rule_id': 'DISCREPANCY_UBO_MISMATCH', 'severity': 'HIGH', 'finding': f'Shareholder {name} ({stake:.0f}% stake) in Commercial Registry is not documented in the UBO Declaration.', 'recommendation': 'Obtain refreshed UBO Declaration and passport copies for all parties with >=25% beneficial interest.'})
    val = profile_data.get('Valid Until') or profile_data.get('valid_until', '')
    if val and re.match(r'\n+4}-\n{2}-\n{2}$', val):
        if val < '2026-10-01':
            flags.append({'rule_id': 'DISCREPANCY_CR_EXPIRED', 'severity': 'HIGH', 'finding': f'Commercial Registration (CR) expired on {val}.', 'recommendation': 'Obtain renewed Commercial Registration Extract from MOCI prior to documentation.'})
    return flags
