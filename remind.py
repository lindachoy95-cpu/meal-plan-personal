"""
Saturday Reminder Script
Emails Linda a reminder with the form link to pick her cuisine for the week.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_ADDRESS      = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
TO_EMAIL           = "lindachoy95@gmail.com"
GITHUB_TOKEN       = os.environ["GITHUB_TOKEN"]
FORM_URL           = f"https://lindachoy95-cpu.github.io/meal-plan-personal/?token={GITHUB_TOKEN}"

html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f7fa;font-family:'Segoe UI',system-ui,sans-serif;">
  <div style="max-width:520px;margin:32px auto;background:white;border-radius:20px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
    <div style="background:linear-gradient(135deg,#1b4332,#2d6a4f);padding:32px;color:white;text-align:center;">
      <div style="font-size:40px;margin-bottom:12px;">🥗</div>
      <h1 style="font-size:1.4rem;margin:0 0 6px;">What are you feeling this week?</h1>
      <p style="opacity:0.8;font-size:0.9rem;margin:0;">Your Sunday meal plan is almost ready — just pick a cuisine!</p>
    </div>
    <div style="padding:32px;text-align:center;">
      <p style="color:#555;font-size:0.95rem;margin-bottom:28px;line-height:1.6;">
        Your weekly meal plan will hit your inbox by <strong>Sunday 6 AM EST</strong>.<br>
        Take 10 seconds to pick what you're craving this week 👇
      </p>
      <a href="{FORM_URL}" style="display:inline-block;background:linear-gradient(135deg,#2d6a4f,#40916c);color:white;text-decoration:none;padding:16px 36px;border-radius:14px;font-weight:700;font-size:1rem;">
        Pick My Cuisine →
      </a>
      <div style="margin-top:24px;display:flex;justify-content:center;gap:16px;flex-wrap:wrap;">
        <span style="font-size:1.4rem;" title="Mediterranean">🫒</span>
        <span style="font-size:1.4rem;" title="Asian">🥢</span>
        <span style="font-size:1.4rem;" title="Mexican">🌮</span>
        <span style="font-size:1.4rem;" title="American">🍗</span>
        <span style="font-size:1.4rem;" title="Surprise me">🌍</span>
      </div>
      <p style="color:#9ca3af;font-size:0.8rem;margin-top:20px;">
        If you don't pick, the agent will choose a varied mix for you.
      </p>
    </div>
    <div style="background:#f9fafb;padding:16px 28px;text-align:center;color:#9ca3af;font-size:12px;border-top:1px solid #f3f4f6;">
      Your Weekly Meal Plan Agent · High Protein · Low Carb · ZIP 11101
    </div>
  </div>
</body>
</html>"""

def send_reminder():
    print("📧 Sending Saturday reminder...")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🥗 Pick your cuisine for this week's meal plan!"
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = TO_EMAIL
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, TO_EMAIL, msg.as_string())
    print("✅ Reminder sent!")

if __name__ == "__main__":
    send_reminder()
