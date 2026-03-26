# 🥗 Weekly Meal Plan Agent

A fully automated AI agent that searches real grocery prices, generates a personalized high-protein low-carb meal plan every week, and emails it to you every Sunday morning.

---

## How it works

1. **Saturday 9 AM** — you get a reminder email with a link to pick your cuisine
2. **You pick your cuisine** — open the form, choose Mediterranean, Asian, Mexican, American, or a mix, hit save
3. **Sunday 7 AM** — the agent wakes up, reads your choice, searches live grocery prices at Trader Joe's, Whole Foods, and H-Mart near ZIP 11101, generates a 7-day meal plan under $100, and emails it to you

---

## 🌐 Cuisine Picker Form

Pick what you're craving each week:
👉 **[Open the form](https://lindachoy95-cpu.github.io/meal-plan-personal)**

---

## Features

- 🔍 Searches **Instacart + web** for real local grocery prices near Long Island City (11101)
- 🧠 AI-generated 7-day meal plan tailored to your chosen cuisine
- 💰 Stays within your **$100 weekly grocery budget**
- 🛒 Shopping list with best store for each item
- 📊 Daily nutrition breakdown (calories, protein, carbs, fat)
- 📧 Delivered to your inbox every Sunday automatically
- 🌮 Pick your cuisine every week — Mediterranean, Asian, Mexican, American, or Varied

---

## Schedule

| Day | Time | What happens |
|-----|------|-------------|
| Saturday | 9 AM EST | Reminder email with form link |
| Saturday/Sunday | Anytime before 7 AM | You fill out the cuisine form |
| Sunday | 7 AM EST | Meal plan generated and emailed |

---

## Tech stack

- **Python** — agent logic
- **Anthropic Claude API** — meal plan generation + web search
- **Gmail SMTP** — email delivery
- **GitHub Actions** — scheduling and automation
- **GitHub Pages** — hosts the cuisine picker form

---

## Files

```
meal-plan-personal/
├── agent.py          # Main Sunday agent — searches prices, generates plan, emails you
├── remind.py         # Saturday reminder — emails you the form link
├── index.html        # Cuisine picker form (hosted on GitHub Pages)
├── requirements.txt  # Python dependencies
└── .github/
    └── workflows/
        └── meal-plan.yml   # Schedules Saturday reminder + Sunday agent
```
