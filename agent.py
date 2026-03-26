"""
Weekly Meal Plan Agent
- Searches for real grocery prices at Trader Joe's, Whole Foods, H-Mart
- Generates a high-protein, low-carb 7-day meal plan within budget
- Emails the plan to yourself every Sunday via Gmail SMTP
"""

import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import anthropic

# ── Config (set these as GitHub Actions secrets) ──────────────────────────────
ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
GMAIL_ADDRESS      = os.environ["GMAIL_ADDRESS"]       # lindachoy95@gmail.com
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]  # Google App Password (NOT your real password)
TO_EMAIL           = "lindachoy95@gmail.com"
WEEKLY_BUDGET      = int(os.environ.get("WEEKLY_BUDGET", "100"))
STORES             = ["Trader Joe's", "Whole Foods", "H-Mart"]

# ── Client ────────────────────────────────────────────────────────────────────
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ── Step 1: Search for grocery prices ─────────────────────────────────────────
def get_grocery_prices() -> str:
    """Use Claude with web search to find current grocery prices."""
    print("🔍 Searching for current grocery prices...")

    stores_str = ", ".join(STORES)
 prompt = f"""Search for grocery prices in NYC at {stores_str}. 
    Find prices for: chicken breast, eggs, salmon, Greek yogurt, spinach, 
    broccoli, canned tuna, olive oil, avocado.
    Return a brief price comparison. Be concise."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )

    price_summary = " ".join(
        block.text for block in response.content if hasattr(block, "text")
    )
    print("✅ Prices gathered.")
    return price_summary


# ── Step 2: Generate meal plan ────────────────────────────────────────────────
def generate_meal_plan(price_summary: str) -> dict:
    """Generate a 7-day meal plan using real prices to stay within budget."""
    print("🧠 Generating meal plan...")

    prompt = f"""You are a nutrition expert and budget-conscious meal planner.

Here are the current grocery prices you found for this week:
{price_summary}

Based on these REAL prices, create a 7-day high-protein, low-carb meal plan for 1 person
with a STRICT weekly grocery budget of ${WEEKLY_BUDGET}.

Preferred stores: {", ".join(STORES)}

Rules:
- Every meal must be high protein, low carb
- Total estimated grocery cost must be at or under ${WEEKLY_BUDGET}
- Prefer the cheapest store for each ingredient based on the prices above
- Reuse ingredients across multiple meals to reduce waste and cost
- Include breakfast, lunch, and dinner each day

Respond ONLY with valid JSON, no markdown:
{{
  "weekOf": "YYYY-MM-DD (this coming Monday's date)",
  "budget": {{
    "limit": {WEEKLY_BUDGET},
    "estimated": <number>,
    "savings": <number>,
    "breakdown": [
      {{"category": "Proteins", "amount": <number>, "store": "best store"}},
      {{"category": "Produce", "amount": <number>, "store": "best store"}},
      {{"category": "Dairy & Fats", "amount": <number>, "store": "best store"}},
      {{"category": "Pantry", "amount": <number>, "store": "best store"}}
    ]
  }},
  "nutrition": {{
    "avgCalories": <number>,
    "avgProtein": <number>,
    "avgCarbs": <number>,
    "avgFat": <number>
  }},
  "days": [
    {{
      "day": "Monday",
      "meals": {{
        "breakfast": {{"name": "...", "protein": <g>, "carbs": <g>}},
        "lunch":     {{"name": "...", "protein": <g>, "carbs": <g>}},
        "dinner":    {{"name": "...", "protein": <g>, "carbs": <g>}}
      }}
    }}
  ],
  "shoppingList": [
    {{"item": "...", "quantity": "...", "estimatedCost": <number>, "bestStore": "..."}}
  ],
  "agentNotes": "2-3 sentences explaining key budget decisions and ingredient reuse strategy"
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.replace("```json", "").replace("```", "").strip()
    plan = json.loads(raw)
    print(f"✅ Meal plan generated. Estimated cost: ${plan['budget']['estimated']}")
    return plan


# ── Step 3: Render HTML email ──────────────────────────────────────────────────
def render_email(plan: dict) -> str:
    """Render a beautiful HTML email from the meal plan."""
    days_html = ""
    for day in plan["days"]:
        days_html += f"""
        <div style="margin-bottom:20px;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
          <div style="background:linear-gradient(90deg,#2d6a4f,#40916c);color:white;padding:10px 16px;font-weight:700;font-size:15px;">
            {day['day']}
          </div>
          <table style="width:100%;border-collapse:collapse;">"""
        for meal_type, meal in day["meals"].items():
            days_html += f"""
            <tr style="border-bottom:1px solid #f3f4f6;">
              <td style="padding:10px 16px;font-weight:700;color:#2d6a4f;width:90px;font-size:12px;text-transform:uppercase;">{meal_type}</td>
              <td style="padding:10px 16px;font-size:14px;color:#1a1a2e;">
                {meal['name']}
                <span style="color:#9ca3af;font-size:12px;margin-left:8px;">{meal['protein']}g protein · {meal['carbs']}g carbs</span>
              </td>
            </tr>"""
        days_html += "</table></div>"

    shopping_rows = "".join(f"""
        <tr style="border-bottom:1px solid #f3f4f6;">
          <td style="padding:8px 12px;font-size:13px;">{item['item']}</td>
          <td style="padding:8px 12px;font-size:13px;color:#6b7280;">{item['quantity']}</td>
          <td style="padding:8px 12px;font-size:13px;color:#2d6a4f;font-weight:600;">{item['bestStore']}</td>
          <td style="padding:8px 12px;font-size:13px;font-weight:700;text-align:right;">~${item['estimatedCost']}</td>
        </tr>""" for item in plan["shoppingList"])

    breakdown_html = "".join(f"""
        <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f3f4f6;font-size:13px;">
          <span style="color:#555;">{b['category']} <span style="color:#9ca3af;font-size:11px;">· {b['store']}</span></span>
          <span style="font-weight:700;">${b['amount']}</span>
        </div>""" for b in plan["budget"]["breakdown"])

    n = plan["nutrition"]
    b = plan["budget"]

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f5f7fa;font-family:'Segoe UI',system-ui,sans-serif;">
  <div style="max-width:620px;margin:32px auto;background:white;border-radius:20px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
    <div style="background:linear-gradient(135deg,#1b4332,#2d6a4f);padding:32px;color:white;">
      <div style="font-size:28px;margin-bottom:6px;">🥗 Your Weekly Meal Plan</div>
      <div style="opacity:0.85;font-size:14px;">Week of {plan['weekOf']} · High Protein · Low Carb</div>
    </div>
    <div style="padding:28px;">
      <div style="display:flex;gap:12px;margin-bottom:24px;background:#f0fdf4;border-radius:12px;padding:16px;">
        <div style="flex:1;text-align:center;"><div style="font-size:22px;font-weight:800;color:#2d6a4f;">{n['avgCalories']}</div><div style="font-size:11px;color:#6b7280;text-transform:uppercase;">Avg Cal/day</div></div>
        <div style="flex:1;text-align:center;"><div style="font-size:22px;font-weight:800;color:#2d6a4f;">{n['avgProtein']}g</div><div style="font-size:11px;color:#6b7280;text-transform:uppercase;">Avg Protein</div></div>
        <div style="flex:1;text-align:center;"><div style="font-size:22px;font-weight:800;color:#2d6a4f;">{n['avgCarbs']}g</div><div style="font-size:11px;color:#6b7280;text-transform:uppercase;">Avg Carbs</div></div>
        <div style="flex:1;text-align:center;"><div style="font-size:22px;font-weight:800;color:#2d6a4f;">{n['avgFat']}g</div><div style="font-size:11px;color:#6b7280;text-transform:uppercase;">Avg Fat</div></div>
      </div>
      <div style="border:1.5px solid #d1fae5;border-radius:12px;padding:18px;margin-bottom:24px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <span style="font-weight:700;font-size:15px;">💰 Grocery Budget</span>
          <span style="font-size:18px;font-weight:800;color:#2d6a4f;">${b['estimated']} / ${b['limit']}</span>
        </div>
        {breakdown_html}
        <div style="margin-top:10px;background:#f0fdf4;border-radius:8px;padding:10px 12px;font-size:13px;color:#059669;">
          ✅ You're saving <strong>${b['savings']}</strong> this week! {plan['agentNotes']}
        </div>
      </div>
      <h2 style="color:#1b4332;font-size:17px;margin:0 0 14px;">📅 7-Day Plan</h2>
      {days_html}
      <h2 style="color:#1b4332;font-size:17px;margin:24px 0 14px;">🛒 Shopping List</h2>
      <table style="width:100%;border-collapse:collapse;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;">
        <thead><tr style="background:#f9fafb;">
          <th style="padding:10px 12px;text-align:left;font-size:12px;color:#6b7280;text-transform:uppercase;">Item</th>
          <th style="padding:10px 12px;text-align:left;font-size:12px;color:#6b7280;text-transform:uppercase;">Qty</th>
          <th style="padding:10px 12px;text-align:left;font-size:12px;color:#6b7280;text-transform:uppercase;">Store</th>
          <th style="padding:10px 12px;text-align:right;font-size:12px;color:#6b7280;text-transform:uppercase;">Cost</th>
        </tr></thead>
        <tbody>{shopping_rows}</tbody>
      </table>
    </div>
    <div style="background:#f9fafb;padding:20px 28px;text-align:center;color:#9ca3af;font-size:12px;border-top:1px solid #f3f4f6;">
      Generated by your Weekly Meal Plan Agent · Every Sunday · High Protein · Low Carb
    </div>
  </div>
</body>
</html>"""


# ── Step 4: Send email via Gmail SMTP ─────────────────────────────────────────
def send_email(html: str, plan: dict):
    """Send the meal plan email to yourself via Gmail."""
    print(f"📧 Sending email to {TO_EMAIL}...")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🥗 Your Meal Plan — Week of {plan['weekOf']} (${plan['budget']['estimated']} groceries)"
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = TO_EMAIL
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, TO_EMAIL, msg.as_string())

    print("✅ Email sent!")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("🚀 Meal Plan Agent starting...")
    prices = get_grocery_prices()
    plan   = generate_meal_plan(prices)
    html   = render_email(plan)
    send_email(html, plan)
    print("✅ Done! Meal plan delivered.")

if __name__ == "__main__":
    main()
