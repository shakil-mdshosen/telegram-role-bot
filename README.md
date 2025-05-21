# 🤖 Telegram Role Mention Bot

A Telegram bot to manage custom **roles** in a group and mention users based on those roles — ideal for communities, task coordination, or team mentions.

---

## 🚀 Features

- ✅ Assign roles to users (`/setrole`)
- ✅ Mention all users with a role (`/mention`)
- ✅ View all current roles (`/roles`)
- ✅ Remove a user from a role (`/removerole`)
- ✅ Delete a role entirely (`/deleterole`)
- ✅ Role list is public to all group members
- ✅ Role changes auto-saved in `roles.json`

---

## 🧑‍💻 Commands

| Command | Description |
|--------|-------------|
| `/start` | Start the bot |
| `/setrole @username role` | Add user to a role (admin only) |
| `/mention role` | Mention all users in that role |
| `/roles` | View all roles and members |
| `/removerole @username role` | Remove user from a role (admin only) |
| `/deleterole role` | Delete a role (admin only) |

Example usage:

```bash
/setrole @alice designer
/mention designer
/removerole @alice designer
/deleterole designer
```

## 🚀 Deployment

You can deploy this bot using **Railway**, **Replit**, or run it **locally**.

---

### 📦 Railway (Recommended)

1. Visit: [https://railway.app](https://railway.app)
2. Click **New Project** → **Deploy from GitHub Repo**
3. Connect your GitHub and select this bot’s repository
4. Go to **Variables** tab and add the following: BOT_TOKEN
5. Ensure your repository contains:
- `main.py` — the bot code
- `Procfile` — tells Railway how to start the bot
- `requirements.txt` — lists Python packages
- `runtime.txt` — defines Python version (e.g., `python-3.10.9`)
6. Click **Deploy** — your bot will go live automatically!
---
