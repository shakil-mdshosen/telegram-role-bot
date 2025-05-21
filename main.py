import os
import json
import requests
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

ROLES_FILE = "roles.json"

# Load roles from JSON file (local)
def load_roles():
    if os.path.exists(ROLES_FILE):
        with open(ROLES_FILE, "r") as f:
            return json.load(f)
    return {}

# Save roles locally
def save_roles():
    with open(ROLES_FILE, "w") as f:
        json.dump(roles, f, indent=2)

# Update roles.json file in GitHub repo via API
def update_github_file():
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")
    path = os.getenv("GITHUB_FILE_PATH", ROLES_FILE)
    branch = os.getenv("GITHUB_BRANCH", "main")

    if not token or not repo:
        print("GitHub token or repo not set. Skipping GitHub update.")
        return

    # Get current file sha (needed to update)
    url_get = f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"
    headers = {"Authorization": f"token {token}"}
    r = requests.get(url_get, headers=headers)
    if r.status_code == 200:
        sha = r.json()["sha"]
    else:
        print(f"Failed to get file SHA from GitHub: {r.status_code} {r.text}")
        sha = None  # for new file create

    # Prepare content base64
    import base64
    content = json.dumps(roles, indent=2)
    content_bytes = content.encode('utf-8')
    content_b64 = base64.b64encode(content_bytes).decode('utf-8')

    url_put = f"https://api.github.com/repos/{repo}/contents/{path}"
    message = "Update roles.json via bot"

    data = {
        "message": message,
        "content": content_b64,
        "branch": branch,
    }
    if sha:
        data["sha"] = sha

    r2 = requests.put(url_put, headers=headers, json=data)
    if r2.status_code in [200,201]:
        print("Successfully updated roles.json on GitHub.")
    else:
        print(f"Failed to update GitHub file: {r2.status_code} {r2.text}")

# Load roles once at startup
roles = load_roles()

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🤖 Role Bot is active!\n"
        "Commands:\n"
        "/setrole @user1 @user2 role\n"
        "/removerole @user1 @user2 role\n"
        "/mention role\n"
        "/roles\n"
        "/deleterole role"
    )

def is_admin(update: Update):
    user_id = update.message.from_user.id
    chat = update.message.chat
    member = chat.get_member(user_id)
    return member.status in ['administrator', 'creator']

def setrole(update: Update, context: CallbackContext):
    if not is_admin(update):
        return update.message.reply_text("❌ Only admins can assign roles.")

    if len(context.args) < 2:
        return update.message.reply_text("Usage: /setrole @user1 @user2 role")

    *usernames, role = context.args
    role = role.lower()
    chat_id = str(update.message.chat_id)

    if chat_id not in roles:
        roles[chat_id] = {}

    if role not in roles[chat_id]:
        roles[chat_id][role] = []

    added_users = []
    for username in usernames:
        username = username.lstrip('@')
        if username not in roles[chat_id][role]:
            roles[chat_id][role].append(username)
            added_users.append(username)

    save_roles()
    update_github_file()

    if added_users:
        added_str = ", ".join(f"@{u}" for u in added_users)
        update.message.reply_text(f"✅ Added {added_str} to role *{role}* in this group.", parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text("ℹ️ All users are already in this role.")

def mention(update: Update, context: CallbackContext):
    if len(context.args) < 1:
        return update.message.reply_text("Usage: /mention role")

    role = context.args[0].lower()
    chat_id = str(update.message.chat_id)

    if chat_id not in roles or role not in roles[chat_id] or not roles[chat_id][role]:
        return update.message.reply_text(f"❌ No users found for role '{role}' in this group.")

    mentions = " ".join([f"@{u}" for u in roles[chat_id][role]])
    update.message.reply_text(f"📢 Members with *{role}* role:\n{mentions}", parse_mode=ParseMode.MARKDOWN)

def show_roles(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat_id)
    if chat_id not in roles or not roles[chat_id]:
        return update.message.reply_text("ℹ️ No roles set for this group yet.")

    message = "📋 *Current Roles in this group:*\n"
    for role, users in roles[chat_id].items():
        user_list = ", ".join([f"@{u}" for u in users])
        message += f"- *{role}*: {user_list}\n"

    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

def removerole(update: Update, context: CallbackContext):
    if not is_admin(update):
        return update.message.reply_text("❌ Only admins can remove users from roles.")

    if len(context.args) < 2:
        return update.message.reply_text("Usage: /removerole @user1 @user2 role")

    *usernames, role = context.args
    role = role.lower()
    chat_id = str(update.message.chat_id)

    if chat_id not in roles or role not in roles[chat_id]:
        return update.message.reply_text(f"❌ Role '{role}' does not exist in this group.")

    removed_users = []
    for username in usernames:
        username = username.lstrip('@')
        if username in roles[chat_id][role]:
            roles[chat_id][role].remove(username)
            removed_users.append(username)

    # If role is empty after removal, delete it
    if role in roles[chat_id] and not roles[chat_id][role]:
        del roles[chat_id][role]

    save_roles()
    update_github_file()

    if removed_users:
        removed_str = ", ".join(f"@{u}" for u in removed_users)
        update.message.reply_text(f"✅ Removed {removed_str} from role *{role}*.", parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text("ℹ️ No specified users were found in the role.")

def deleterole(update: Update, context: CallbackContext):
    if not is_admin(update):
        return update.message.reply_text("❌ Only admins can delete roles.")

    if len(context.args) < 1:
        return update.message.reply_text("Usage: /deleterole role")

    role = context.args[0].lower()
    chat_id = str(update.message.chat_id)

    if chat_id in roles and role in roles[chat_id]:
        del roles[chat_id][role]
        save_roles()
        update_github_file()
        update.message.reply_text(f"🗑️ Role *{role}* deleted in this group.", parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text(f"❌ Role '{role}' does not exist in this group.")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("❌ Error: BOT_TOKEN not found in environment variables.")
        return

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setrole", setrole))
    dp.add_handler(CommandHandler("mention", mention))
    dp.add_handler(CommandHandler("roles", show_roles))
    dp.add_handler(CommandHandler("removerole", removerole))
    dp.add_handler(CommandHandler("deleterole", deleterole))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
