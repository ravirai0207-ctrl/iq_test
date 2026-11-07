"""
Email and OTP Delivery Module.
Supports real SMTP (e.g. Gmail, Outlook, Sendgrid, custom SMTP)
with seamless dev/fallback mode for instant local testing.
"""

import os
import json
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smtp_config.json")


def load_smtp_config():
    """Load SMTP settings from smtp_config.json or environment."""
    defaults = {
        "enabled": False,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "",
        "smtp_pass": "",
        "from_email": "noreply-iqtest@cognitivelabs.ai",
        "from_name": "CognitiveIQ Assessment Labs"
    }

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                defaults.update(loaded)
        except Exception as e:
            print(f"[Mailer] Warning loading config: {e}")

    # Environment variable overrides
    if os.environ.get("SMTP_HOST"):
        defaults["smtp_host"] = os.environ.get("SMTP_HOST")
        defaults["enabled"] = True
    if os.environ.get("SMTP_PORT"):
        try:
            defaults["smtp_port"] = int(os.environ.get("SMTP_PORT"))
        except ValueError:
            pass
    if os.environ.get("SMTP_USER"):
        defaults["smtp_user"] = os.environ.get("SMTP_USER")
    if os.environ.get("SMTP_PASS"):
        defaults["smtp_pass"] = os.environ.get("SMTP_PASS")
    if os.environ.get("SMTP_FROM"):
        defaults["from_email"] = os.environ.get("SMTP_FROM")

    return defaults


def generate_otp(length=6) -> str:
    """Generate a cryptographically secure numeric OTP."""
    digits = "0123456789"
    return "".join(secrets.choice(digits) for _ in range(length))


def get_otp_expiry(minutes=10) -> str:
    """Return ISO timestamp for OTP expiration."""
    return (datetime.now() + timedelta(minutes=minutes)).isoformat()


def send_otp_email(recipient_email: str, recipient_name: str, otp_code: str) -> dict:
    """
    Sends the OTP verification email to recipient.
    If SMTP is not enabled or fails, falls back to dev simulation mode.
    """
    cfg = load_smtp_config()
    smtp_enabled = cfg.get("enabled", False) and bool(cfg.get("smtp_user")) and bool(cfg.get("smtp_pass"))

    subject = f"Your Cognitive IQ Verification Code: {otp_code}"
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f6fc; margin: 0; padding: 20px; }}
    .container {{ max-width: 520px; margin: 20px auto; background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
    .header {{ background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); padding: 32px 24px; text-align: center; color: #ffffff; }}
    .header h1 {{ margin: 0; font-size: 22px; font-weight: 700; letter-spacing: 0.5px; }}
    .header p {{ margin: 6px 0 0; font-size: 13px; opacity: 0.9; }}
    .body {{ padding: 32px 28px; color: #1e293b; line-height: 1.6; }}
    .greeting {{ font-size: 16px; font-weight: 600; margin-bottom: 12px; }}
    .otp-card {{ background: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 12px; padding: 20px; text-align: center; margin: 24px 0; }}
    .otp-code {{ font-size: 36px; font-weight: 800; letter-spacing: 10px; color: #4338ca; font-family: monospace; }}
    .expiry {{ font-size: 12px; color: #64748b; margin-top: 8px; }}
    .footer {{ background: #f1f5f9; padding: 18px 24px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>NEURAL COGNITIVE LABS</h1>
      <p>Official 3D Standardized IQ Assessment</p>
    </div>
    <div class="body">
      <div class="greeting">Hello {recipient_name},</div>
      <p>You have registered for the 3D Cognitive IQ Examination. Please use the verification code below to validate your email address and unlock your test session:</p>
      
      <div class="otp-card">
        <div class="otp-code">{otp_code}</div>
        <div class="expiry">Expires in 10 minutes. Do not share this code.</div>
      </div>
      
      <p style="font-size: 13px; color: #475569;">
        Once verified, you will be directed to the calibration matrix where your fluid intelligence, pattern logic, and spatial reasoning will be evaluated.
      </p>
    </div>
    <div class="footer">
      Sent to {recipient_email} • CognitiveIQ Neuro-Testing Engine
    </div>
  </div>
</body>
</html>
"""

    text_content = f"Hello {recipient_name},\n\nYour 3D IQ Test verification code is: {otp_code}\nThis code expires in 10 minutes.\n\nCognitiveIQ Neuro-Testing Labs"

    if smtp_enabled:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{cfg.get('from_name')} <{cfg.get('from_email')}>"
            msg["To"] = recipient_email
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            port = cfg.get("smtp_port", 587)
            host = cfg.get("smtp_host", "smtp.gmail.com")

            if port == 465:
                server = smtplib.SMTP_SSL(host, port, timeout=10)
            else:
                server = smtplib.SMTP(host, port, timeout=10)
                server.ehlo()
                server.starttls()
                server.ehlo()

            server.login(cfg.get("smtp_user"), cfg.get("smtp_pass"))
            server.sendmail(cfg.get("from_email"), [recipient_email], msg.as_string())
            server.quit()

            print(f"[Mailer] Successfully sent OTP email to {recipient_email} via SMTP ({host})")
            return {
                "success": True,
                "mode": "smtp",
                "message": f"Verification code sent to {recipient_email}"
            }
        except Exception as e:
            print(f"[Mailer] SMTP send failed: {e}. Falling back to simulation mode.")
            return {
                "success": True,
                "mode": "dev_simulation",
                "otp_preview": otp_code,
                "message": f"Verification code generated (Dev mode: {otp_code})"
            }
    else:
        # Development / Local testing mode
        print(f"\n==========================================")
        print(f"[DEV MAILER] To: {recipient_email} ({recipient_name})")
        print(f"[DEV MAILER] 🔑 OTP CODE: >>> {otp_code} <<<")
        print(f"[DEV MAILER] (Set smtp_config.json to send real emails via your inbox)")
        print(f"==========================================\n")
        return {
            "success": True,
            "mode": "dev_simulation",
            "otp_preview": otp_code,
            "message": f"Verification code sent (Dev Preview: {otp_code})"
        }

