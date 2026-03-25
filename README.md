# 🥗 Weekly Meal Plan Agent

An AI agent that searches real grocery prices at Trader Joe's, Whole Foods, and H-Mart,
generates a high-protein low-carb 7-day meal plan within your $100 budget, and emails
it to lindachoy95@gmail.com every Sunday morning — no new accounts needed.

---

## How it works

1. **Searches the web** for current grocery prices at your stores in NYC
2. **Generates a meal plan** using Claude, staying within your $100 budget
3. **Emails you** a formatted meal plan + shopping list every Sunday via your own Gmail

---

## Setup (one time, ~10 minutes)

### Step 1 — Get your Anthropic API key

1. Go to https://console.anthropic.com → API Keys
2. Create a new key and copy it

### Step 2 — Create a Gmail App Password

This lets the script send email FROM your Gmail without using your real password.

1. Go to https://myaccount.google.com/security
2. Make sure **2-Step Verification** is turned ON
3. Search for "App passwords" at the top of that page
4. Click App passwords → create one named "Meal Plan Agent"
5. Copy the 16-character password it gives you

> ⚠️ This is NOT your Gmail password. It's a separate one-time code just for this app.

### Step 3 — Put this code on GitHub

1. Go to https://github.com/new → create a **private** repository
2. Upload all these files to it (drag and drop works)

### Step 4 — Add your secrets to GitHub

1. In your repo, go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret** and add each of these:

| Secret name        | Value                              |
|--------------------|------------------------------------|
| `ANTHROPIC_API_KEY`| Your Anthropic key                 |
| `GMAIL_ADDRESS`    | lindachoy95@gmail.com              |
| `GMAIL_APP_PASSWORD`| The 16-character app password     |
| `WEEKLY_BUDGET`    | 100                                |

> ✅ Your real Gmail password is never used or stored anywhere.

### Step 5 — Test it manually

1. Go to your GitHub repo → **Actions** tab
2. Click **Weekly Meal Plan Agent** → **Run workflow**
3. Check lindachoy95@gmail.com in ~60 seconds!

---

## Schedule

Runs every **Sunday at 10:00 AM UTC (6:00 AM EST)** automatically.

To change the time, edit `.github/workflows/meal-plan.yml`:
```yaml
- cron: '0 10 * * 0'   # minute hour day month weekday
```

---

## Files

```
meal-agent/
├── agent.py                          # The main agent script
├── requirements.txt                  # Python dependencies (just anthropic)
├── README.md                         # This file
└── .github/
    └── workflows/
        └── meal-plan.yml             # GitHub Actions schedule
```
