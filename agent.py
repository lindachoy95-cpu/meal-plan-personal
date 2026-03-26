"""
Weekly Meal Plan Agent
- Searches for real grocery prices at Trader Joe's, Whole Foods, H-Mart
- Generates a high-protein, low-carb 7-day meal plan within budget
- Emails the plan to yourself every Sunday via Gmail SMTP
"""

import os
import json
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import anthropic

# ── Config (set these as GitHub Actions secrets) ──────────────────────────────
ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
GMAIL_ADDRESS      = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
TO_EMAIL           = "lindachoy95@gmail.com"
WEEKLY_BUDGET      = int(os.environ.get("WEEKLY_BUDGET", "100"))
STORES             = ["Trader Joe's", "Whole Foods", "H-Mart"]

# ── Client ────────────────────────────────────────────────────────────────────
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ── Step 1: Search for grocery prices ─────────────────────────────────────────
def get_grocery_prices() -> str:
    print("🔍 Searching for current grocery prices...")
    stores_str = ", ".join(STORES)
    prompt = f"""Search for grocery prices in NYC at {stores_str}.
Find prices for: chicken breast, eggs, salmon, Greek yogurt, spinach, broccoli, canned tuna, olive oil, avocado.
Return a brief price comparison. Be concise."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
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
    print("🧠 Generating meal plan...")
    prompt = f"""Create a 7-day high-protein low-carb meal plan for 1 person, budget ${WEEKLY_BUDGET}/week.
Prices this week: {price_summary[:500]}
Preferred stores: {", ".join(STORES)}

Rules: high protein, low carb every meal. Stay under ${WEEKLY_BUDGET}. Reuse ingredients.

Respond ONLY with valid JSON, no markdown:
{{
  "weekOf": "2026-03-30",
  "budget": {{
    "limit": {WEEKLY_BUDGET},
    "estimated": 85,
    "savings": 15,
    "breakdown": [
      {{"category": "Proteins", "amount": 45, "store": "Trader Joe's"}},
      {{"category": "Produce", "amount": 20, "store": "H-Mart"}},
      {{"category": "Dairy & Fats", "amount": 12, "store": "Trader Joe's"}},
      {{"category": "Pantry", "amount": 8, "store": "Whole Foods"}}
    ]
  }},
  "nutrition": {{"avgCalories": 1800, "avgProtein": 150, "avgCarbs": 50, "avgFat": 80}},
  "days": [
    {{"day": "Monday", "meals": {{"breakfast": {{"name": "Greek yogurt with almonds", "protein": 20, "carbs": 10}}, "lunch": {{"name": "Tuna salad over spinach", "protein": 35, "carbs": 5}}, "dinner": {{"name": "Grilled chicken with broccoli", "protein": 45, "carbs": 10}}}}}},
    {{"day": "Tuesday", "meals": {{"breakfast": {{"name": "Scrambled eggs with spinach", "protein": 18, "carbs": 3}}, "lunch": {{"name": "Salmon salad", "protein": 38, "carbs": 5}}, "dinner": {{"name": "Ground beef stir fry with zucchini", "protein": 42, "carbs": 8}}}}}},
    {{"day": "Wednesday", "meals": {{"breakfast": {{"name": "Cottage cheese with avocado", "protein": 22, "carbs": 8}}, "lunch": {{"name": "Chicken lettuce wraps", "protein": 36, "carbs": 6}}, "dinner": {{"name": "Baked salmon with asparagus", "protein": 44, "carbs": 7}}}}}},
    {{"day": "Thursday", "meals": {{"breakfast": {{"name": "Eggs and turkey bacon", "protein": 24, "carbs": 2}}, "lunch": {{"name": "Tuna and avocado bowl", "protein": 34, "carbs": 6}}, "dinner": {{"name": "Chicken thighs with roasted broccoli", "protein": 46, "carbs": 9}}}}}},
    {{"day": "Friday", "meals": {{"breakfast": {{"name": "Greek yogurt parfait", "protein": 20, "carbs": 12}}, "lunch": {{"name": "Ground beef lettuce tacos", "protein": 38, "carbs": 5}}, "dinner": {{"name": "Shrimp stir fry with cauliflower rice", "protein": 40, "carbs": 10}}}}}},
    {{"day": "Saturday", "meals": {{"breakfast": {{"name": "Omelette with cheese and spinach", "protein": 22, "carbs": 3}}, "lunch": {{"name": "Salmon and cucumber salad", "protein": 36, "carbs": 5}}, "dinner": {{"name": "Grilled chicken thighs with green beans", "protein": 44, "carbs": 8}}}}}},
    {{"day": "Sunday", "meals": {{"breakfast": {{"name": "Smoked salmon and eggs", "protein": 28, "carbs": 2}}, "lunch": {{"name": "Chicken and avocado salad", "protein": 38, "carbs": 7}}, "dinner": {{"name": "Beef and broccoli bowl", "protein": 45, "carbs": 10}}}}}}
  ],
  "shoppingList": [
    {{"item": "Chicken breast 3lb", "quantity": "1 pack", "estimatedCost": 12, "bestStore": "Trader Joe's"}},
    {{"item": "Ground beef 1lb", "quantity": "2 packs", "estimatedCost": 14, "bestStore": "Trader Joe's"}},
    {{"item": "Salmon fillets", "quantity": "1lb", "estimatedCost": 10, "bestStore": "H-Mart"}},
    {{"item": "Eggs", "quantity": "12 pack", "estimatedCost": 4, "bestStore": "Trader Joe's"}},
    {{"item": "Greek yogurt", "quantity": "32oz", "estimatedCost": 5, "bestStore": "Trader Joe's"}},
    {{"item": "Canned tuna", "quantity": "4 cans", "estimatedCost": 6, "bestStore": "Trader Joe's"}},
    {{"item": "Spinach", "quantity": "5oz bag", "estimatedCost": 3, "bestStore": "H-Mart"}},
    {{"item": "Broccoli", "quantity": "2 heads", "estimatedCost": 4, "bestStore": "H-Mart"}},
    {{"item": "Avocado", "quantity": "3 pack", "estimatedCost": 5, "bestStore": "Trader Joe's"}},
    {{"item": "Olive oil", "quantity": "1 bottle", "estimatedCost": 8, "bestStore": "Trader Joe's"}}
  ],
  "agentNotes": "Chicken and eggs are reused across multiple meals to minimize cost. H-Mart offers the best prices on fresh produce and salmon this week."
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.replace("```json", "").replace("```", "").strip()
    plan = json.loads(raw)
    print(f"✅ Meal plan generated. Estimated cost: ${plan['budget']['estimated']}")
    return plan


# ── Step 3: Render HTML email ──────────────────────────────────────────────────
def render_email(plan: dict) -> str:
    days_html = ""
    for day in plan["days"]:
        days_html += f"""
        <div style="margin-bottom:20px;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
          <div style="background:linear-gradient(90deg,#2d6a4f,#40916c);color:white;padding:10px 16px;font-weight:700;font-size:15px;">{day['day']}</div>
          <table style="width:100%;border-collapse:collapse;">"""
        for meal_type, meal in day["meals"].items():
            days_html += f"""
            <tr style="border-bottom:1px solid #f3f4f6;">
              <td style="padding:10px 16px;font-weight:700;color:#2d6a4f;width:90px;font-size:12px;text-transform:uppercase;">{meal_type}</td>
              <td style="padding:10px 16px;font-size:14px;color:#1a1a2e;">{meal['name']}
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
    print("⏳ Waiting 60 seconds to avoid rate limits...")
    time.sleep(60)
    plan = generate_meal_plan(prices)
    html = render_email(plan)
    send_email(html, plan)
    print("✅ Done! Meal plan delivered.")

if __name__ == "__main__":
    main()
