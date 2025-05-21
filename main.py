import os
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# In-memory role storage
# Format: { "role_name": {"username1", "username2"} }
roles = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Bot is running! Use /setrole, /mention, /roles to manage user roles.")

def setrole(update: Update, context: CallbackContext):
    user_status = update.message.chat.get_member(update.message.from_user.id).status
    if user_status not in ['administrator', 'creator']:
        update.message.reply_text("❌ Only admins can assign roles.")
        return

    if len(context.args) < 2:
        update.message.reply_text("Usage: /setrole @username role")
        return

    username = context.args[0].lstrip('@')
    role = context.args[1].lower()

    if role not in roles:
        roles[role] = set()
    roles[role].add(username)

    update.message.reply_text(f"✅ @{username} added to role *{role}*", parse_mode=ParseMode.MARKDOWN)

def mention(update: Update, context: CallbackContext):
    if len(context.args) < 1:
        update.message.reply_text("Usage: /mention role")
        return

    role = context.args[0].lower()
    if role not in roles or not roles[role]:
        update.message.reply_text(f"❌ No users found for role '{role}'.")
        return

    mentions = " ".join([f"@{u}" for u in roles[role]])
    update.message.reply_text(f"📢 Members with *{role}* role:\n{mentions}", parse_mode=ParseMode.MARKDOWN)

def show_roles(update: Update, context: CallbackContext):
    if not roles:
        update.message.reply_text("ℹ️ No roles have been set yet.")
        return

    message = "📋 *Current Roles:*\n"
    for role, users in roles.items():
        user_list = ", ".join([f"@{u}" for u in users])
        message += f"- *{role}*: {user_list}\n"

    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN not found in environment variables.")
        return

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setrole", setrole))
    dp.add_handler(CommandHandler("mention", mention))
    dp.add_handler(CommandHandler("roles", show_roles))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
