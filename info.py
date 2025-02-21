from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions, CallbackQuery
from pyrogram.enums import ChatMemberStatus

API_ID = 28795512  # अपने Telegram API ID से बदलें
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"  # अपने Telegram API Hash से बदलें
BOT_TOKEN = "7589052839:AAGPMVeZpb63GEG_xXzQEua1q9ewfNzTg50"

app = Client("moderation_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ **Ban, Mute, Warn Actions (Callback)**
@app.on_callback_query(filters.regex(r"action_(\w+)_(\d+)"))
async def handle_actions(client: Client, query: CallbackQuery):
    action, user_id = query.matches[0].group(1), int(query.matches[0].group(2))
    chat_id = query.message.chat.id

    try:
        if action == "ban":
            await client.ban_chat_member(chat_id, user_id)
            await query.answer("🚫 यूजर बैन कर दिया गया!", show_alert=True)
        elif action == "mute":
            await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
            await query.answer("🔇 यूजर म्यूट कर दिया गया!", show_alert=True)
        elif action == "warn":
            warning_text = f"⚠️ चेतावनी: <a href='tg://user?id={user_id}'>यह यूजर</a> नियम तोड़ रहा है!"
            await client.send_message(chat_id, warning_text, parse_mode="html")
            await query.answer("⚠️ यूजर को चेतावनी दी गई!", show_alert=True)
        else:
            await query.answer("❌ कोई एक्शन नहीं मिला!", show_alert=True)
    except Exception as e:
        await query.answer(f"❌ एरर: {e}", show_alert=True)

# ✅ **Admin Panel (Ban, Mute, Warn, Profile)**
@app.on_message(filters.command("adminpanel") & filters.group)
async def admin_panel(client, message):
    if not message.reply_to_message:
        await message.reply_text("❌ कृपया पहले किसी यूजर को रिप्लाई करें।")
        return

    user = message.reply_to_message.from_user

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚫 Ban", callback_data=f"action_ban_{user.id}"),
            InlineKeyboardButton("🔇 Mute", callback_data=f"action_mute_{user.id}")
        ],
        [
            InlineKeyboardButton("⚠️ Warn", callback_data=f"action_warn_{user.id}"),
            InlineKeyboardButton("👤 Info", callback_data=f"action_info_{user.id}")
        ],
        [
            InlineKeyboardButton("🔍 Profile", url=f"https://t.me/{user.username}") if user.username else InlineKeyboardButton("❌ कोई यूजरनेम नहीं", callback_data="no_username")
        ]
    ])

    await message.reply_text(f"🔧 <b>मॉडरेशन पैनल</b> - {user.mention}", reply_markup=buttons, parse_mode="html")

# ✅ **User Full Information (Fixes)**
@app.on_callback_query(filters.regex(r"action_info_(\d+)"))
async def user_info(client, query: CallbackQuery):
    user_id = int(query.matches[0].group(1))
    chat_id = query.message.chat.id
    chat_member = await client.get_chat_member(chat_id, user_id)
    user = chat_member.user

    is_muted = (
        chat_member.status == ChatMemberStatus.RESTRICTED and
        chat_member.privileges and not chat_member.privileges.can_send_messages
    )

    warnings = 0  # चेतावनियों की संख्या (डेमो के लिए)

    text = (
        "📜 User Full Information 📜\n\n"
        f"🆔 ID: {user.id}\n"
        f"🐱 Name: {user.first_name or 'No Name'}\n"
        f"🌍 Username: @{user.username if user.username else 'No username'}\n"
        f"👀 Situation: {'Admin' if chat_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] else 'Member'}\n"
        f"⚠️ Warnings: {warnings}/3\n"
        f"🔇 Muted: {'Yes' if is_muted else 'No'}\n"
        f"⏳ Join Date: {chat_member.joined_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(chat_member, 'joined_date') and chat_member.joined_date else 'Unknown'}\n"
    )

    await query.message.reply_text(text)

# ✅ **Bot Run (एरर फिक्स)**
if __name__ == "__main__":
    print("🤖 Bot is running...")
    app.run()
