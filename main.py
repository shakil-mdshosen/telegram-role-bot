import os
import json
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

ROLES_FILE = "roles.json"

# Load roles from JSON file
def load_roles():
    if os.path.exists(ROLES_FILE):
        with open(ROLES_FILE, "r") as f:
            return json.load(f)
    return {}

# Save roles to JSON file
def save_roles():
    with open(ROLES_FILE, "w") as f:
        json.dump(roles, f)

# Initialize roles
roles = load_roles()

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Role Bot is active!\nUse /setrole, /mention, /roles, /removerole, /deleterole.")

def is_admin(update: Update):
    user_id = update.message.from_user.id
    chat = update.message.chat
    status = chat.get_member(user_id).status
    return status in ['administrator', 'creator']

def setrole(update: Update, context: CallbackContext):
    if not is_admin(update):
        return update.message.reply_text("❌ Only admins can assign roles.")

    if len(context.args) < 2:
        return update.message.reply_text("Usage: /setrole @username role")

    username = context.args[0].lstrip('@')
    role = context.args[1].lower()

    if role not in roles:
        roles[role] = []
    if username not in roles[role]:
        roles[role].append(username)
        save_roles()

    update.message.reply_text(f"✅ @{username} added to role *{role}*", parse_mode=ParseMode.MARKDOWN)

def mention(update: Update, context: CallbackContext):
    if len(context.args) < 1:
        return update.message.reply_text("Usage: /mention role")

    role = context.args[0].lower()
    if role not in roles or not roles[role]:
        return update.message.reply_text(f"❌ No users found for role '{role}'.")

    mentions = " ".join([f"@{u}" for u in roles[role]])
    update.message.reply_text(f"📢 Members with *{role}* role:\n{mentions}", parse_mode=ParseMode.MARKDOWN)

def show_roles(update: Update, context: CallbackContext):
    if not roles:
        return update.message.reply_text("ℹ️ No roles have been set yet.")

    message = "📋 *Current Roles:*\n"
    for role, users in roles.items():
        user_list = ", ".join([f"@{u}" for u in users])
        message += f"- *{role}*: {user_list}\n"

    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

def removerole(update: Update, context: CallbackContext):
    if not is_admin(update):
        return update.message.reply_text("❌ Only admins can remove users from roles.")

    if len(context.args) < 2:
        return update.message.reply_text("Usage: /removerole @username role")

    username = context.args[0].lstrip('@')
    role = context.args[1].lower()

    if role in roles and username in roles[role]:
        roles[role].remove(username)
        if not roles[role]:  # Remove role if empty
            del roles[role]
        save_roles()
        return update.message.reply_text(f"✅ Removed @{username} from role *{role}*", parse_mode=ParseMode.MARKDOWN)

    update.message.reply_text(f"❌ @{username} is not in role '{role}'")

def deleterole(update: Update, context: CallbackContext):
    if not is_admin(update):
        return update.message.reply_text("❌ Only admins can delete roles.")

    if len(context.args) < 1:
        return update.message.reply_text("Usage: /deleterole role")

    role = context.args[0].lower()

    if role in roles:
        del roles[role]
        save_roles()
        return update.message.reply_text(f"🗑️ Role *{role}* deleted.", parse_mode=ParseMode.MARKDOWN)

    update.message.reply_text(f"❌ Role '{role}' does not exist.")

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
