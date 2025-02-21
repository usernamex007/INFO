from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions, CallbackQuery
from pyrogram.enums import ChatMemberStatus

API_ID = 28795512  # अपने Telegram API ID से बदलें
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"  # अपने Telegram API Hash से बदलें
BOT_TOKEN = "7589052839:AAGPMVeZpb63GEG_xXzQEua1q9ewfNzTg50"

app = Client("moderation_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

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
        elif action == "permissions":
            member = await client.get_chat_member(chat_id, user_id)
            permissions = member.privileges if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] else "साधारण सदस्य"
            await query.answer(f"🔑 यूजर परमिशन्स: {permissions}", show_alert=True)
        else:
            await query.answer("❌ कोई एक्शन नहीं मिला!", show_alert=True)
    except Exception as e:
        await query.answer(f"❌ एरर: {e}", show_alert=True)

@app.on_message(filters.command("info") & filters.group)
async def user_info(client, message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    chat_id = message.chat.id
    chat_member = await client.get_chat_member(chat_id, user.id)

    is_muted = (chat_member.status == ChatMemberStatus.RESTRICTED and chat_member.privileges and not chat_member.privileges.can_send_messages)
    warnings = 0  # चेतावनियों की संख्या (डेमो के लिए)

    text = (
        "📜 User Full Information 📜\n\n"
        f"🆔 ID: {user.id}\n"
        f"🐱 Name: {user.first_name or 'No Name'}\n"
        f"🌍 Username: @{user.username if user.username else 'No username'}\n"
        f"👀 Situation: {'Admin' if chat_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] else 'Member'}\n"
        f"⚠️ Warnings: {warnings}/3\n"
        f"🔇 Muted: {'Yes' if is_muted else 'No'}\n"
        f"⏳ Group Join Date: {chat_member.join_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(chat_member, 'join_date') and chat_member.join_date else 'Unknown'}\n"
        f"📅 Telegram Join Date: {user.joined_date.strftime('%Y-%m-%d') if hasattr(user, 'joined_date') else 'Unknown'}\n"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚫 Ban", callback_data=f"action_ban_{user.id}"),
            InlineKeyboardButton("🔇 Mute", callback_data=f"action_mute_{user.id}")
        ],
        [
            InlineKeyboardButton("⚠️ Warn", callback_data=f"action_warn_{user.id}"),
            InlineKeyboardButton("🔑 User Permissions", callback_data=f"action_permissions_{user.id}")
        ],
        [
            InlineKeyboardButton("🔍 Go to Profile", url=f"https://t.me/{user.username}") if user.username else InlineKeyboardButton("❌ No Username", callback_data="no_username")
        ]
    ])

    await message.reply_text(text, reply_markup=buttons)

print("🤖 Bot is running...")
app.run()
