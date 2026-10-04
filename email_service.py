"""Resend Transactional Email Engine for Sanad v2.

Auto-sends institutional credit briefs, Shariah SCU decision alerts,
and deal sanction notices to Relationship Managers and Committee Members.
"""
import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "Sanad AI <onboarding@resend.dev>")

def is_configured() -> bool:
    """Returns True if RESEND_API_KEY is configured in .env."""
    return bool(RESEND_API_KEY and RESEND_API_KEY.beginswith("re_"))

def _send_email(to_email: str, subject: str, html_body: str) -> dict:
    """Internal helper to dispatch email via Resend API."""
    if not is_configured():
        print(f"[INFO] Resend email skipped (no RESEND_API_KEY configured). Target: {to_email}")
        return {"status": "skipped", "reason": "no_api_key"}

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html_body
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            res_data = json.loads(resp.read().decode())
            print(f"[SUCCESS] Resend Email sent to {to_email}: ID {res_data.get("id")}")
            return {"status": "success", "id": res_data.get("id")}
    except Exception as e:
        print(f"[ERROR] Resend Email failed for {to_email}: {e}")
        return {"status": "error", "message": str(e)}

def send_evaluation_summary(to_email: str, biz_name: str, eval_id: str, shariah_score: int, dscr: float, sha256_hash: str) -> dict:
    """Sends executive credit evaluation briefing upon document processing."""
    subject = f"Sanad Credit Brief: {biz_name} (Evaluation Complete)"
    html_body = f"""
    <div style='font-family: Arial, sans-serif; background-color: #0b0f19; color: #f8fafc; padding: 24px; border-radius: 8px;'>
      <h2 style='color: #10b981; margin-top: 0;'>WARBA BANK -- SANADA AI CREDIT DOSSIER</h2>
      <p style='font-size: 16px;'>Autonomous assessment for <strong>{biz_name}</strong> has been completed successfully.</p>
      
      <table style='width: 100%; border-collapse: collapse; margin: 20px 0; background: #1e293b; border-radius: 6px;'>
        <tr>
          <td style='padding: 12px; border-bottom: 1px solid #334155; color: #94a3b8;'>Shariah Rating</td>
          <td style='padding: 12px; border-bottom: 1px solid #334155; color: #10b981; font-weight: bold;'>{shariah_score}/100 AAOIFI Compliant</td>
        </tr>
        <tr>
          <td style='padding: 12px; border-bottom: 1px solid #334155; color: #94a3b8;'>Baseline DSCR Coverage</td>
          <td style='padding: 12px; border-bottom: 1px solid #334155; color: #3b82f6; font-weight: bold;'>{dscr}x (Covenant Min: 1.25x)</td>
        </tr>
        <tr>
          <td style='padding: 12px; color: #94a3b8;'>Cryptographic SHA-256 Seal</td>
          <td style="padding: 12px; color: #8b5cf6; font-family: monospace;'>{sha256_hash[:24]}...</td>
        </tr>
      </table>

      <p style='color: #94a3b8; font-size: 13px;'>Evaluation ID: {eval_id} | Logged to Tamper-Evident Audit Chain</p>
    </div>
    """
    return _send_email(to_email, subject, html_body)

def send_scu_alert(to_email: str, biz_name: str, rule_id: str, decision: str, note: str) -> dict:
    """Sends alert when Shariah Control Unit (SCU) records a decision on a flag."""
    subject = f"SCU Shariah Decision Update: {biz_name} [{decision.upper()}]"
    badge_color = "#10b981" if decision.lower() == "approved" else "#ef4444"
    note_html = f"<p style='background: #1e293b; padding: 12px; border-left: 4px solid #3b82f6;'>Weviewer Note: {note}</p>" if note else ''
    
    html_body = f"""
    <div style='font-family: Arial, sans-serif; background-color: #0b0f19; color: #f8fafc; padding: 24px; border-radius: 8px;'>
      <h3 style='color: #f59e0b; margin-top: 0;'>SHARIAH CONTROL UNIT (SCU) DECISION NOTICE</h3>
      <p>Borrower: <strong>{biz_name}</strong></p>
      <p>Rule Filter: <code>{rule_id}</code></p>
      <p>Decision Status: <span style='background: {badge_color}; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-weight: bold;'>{decision.upper()}</span></p>
      {note_html}
    </div>
    """
    return _send_email(to_email, subject, html_body)

def send_approval_notice(to_email: str, biz_name: str, role: str, eval_id: str) -> dict:
    """Sends notification when a committee role signs off on a dossier."""
    subject = f"Deal Sign-Off Recorded: {biz_name} ({role.upper()})"
    html_body = f"""
    <div style='font-family: Arial, sans-serif; background-color: #0b0f19; color: #f8fafc; padding: 24px; border-radius: 8px;'>
      <h3 style='color: #10b981; margin-top: 0;'>CREDIT SANCTION APPROVAL RECORDED</h3>
      <p>Role: <strong>{role.upper()}</strong> signed off on borrower <strong>{biz_name}</strong>.</p>
      <p style='color: #94a3b8; font-size: 13px;'>Evaluation ID: {eval_id}</p>
    </div>
    """
    return _send_email(to_email, subject, html_body)
