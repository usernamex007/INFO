from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from pyrogram.enums import ChatMemberStatus

# बॉट की डिटेल्स
API_ID = 28795512  # अपने Telegram API ID से बदलें
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"  # अपने Telegram API Hash से बदलें
BOT_TOKEN = "7589052839:AAGPMVeZpb63GEG_xXzQEua1q9ewfNzTg50"  # अपने Bot Token से बदलें

app = Client("moderation_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ **Permission Checker**
def is_admin(_, __, message):
    chat_member = app.get_chat_member(message.chat.id, message.from_user.id)
    return chat_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]

# ✅ **Ban User**
@app.on_callback_query(filters.regex("ban_(\\d+)"))
async def ban_user(client, callback_query):
    user_id = int(callback_query.matches[0].group(1))
    chat_id = callback_query.message.chat.id

    try:
        await client.ban_chat_member(chat_id, user_id)
        await callback_query.answer("🚫 यूजर को बैन कर दिया गया!", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"❌ एरर: {e}", show_alert=True)

# ✅ **Mute User**
@app.on_callback_query(filters.regex("mute_(\\d+)"))
async def mute_user(client, callback_query):
    user_id = int(callback_query.matches[0].group(1))
    chat_id = callback_query.message.chat.id

    try:
        await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
        await callback_query.answer("🔇 यूजर म्यूट कर दिया गया!", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"❌ एरर: {e}", show_alert=True)

# ✅ **Warn User**
@app.on_callback_query(filters.regex("warn_(\\d+)"))
async def warn_user(client, callback_query):
    user_id = int(callback_query.matches[0].group(1))
    chat_id = callback_query.message.chat.id

    try:
        warning_text = f"⚠️ चेतावनी: <a href='tg://user?id={user_id}'>यह यूजर</a> नियम तोड़ रहा है!"
        await client.send_message(chat_id, warning_text, parse_mode="html")
        await callback_query.answer("⚠️ यूजर को चेतावनी दी गई!", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"❌ एरर: {e}", show_alert=True)

# ✅ **Go to Profile Button**
@app.on_message(filters.command("profile") & filters.group)
async def profile_button(client, message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 प्रोफाइल पर जाएं", url=f"https://t.me/{user.username}") if user.username else InlineKeyboardButton("❌ यूजरनेम उपलब्ध नहीं", callback_data="no_username")]
    ])
    
    await message.reply_text("🔗 प्रोफाइल लिंक:", reply_markup=button)

# ✅ **Check Permissions**
@app.on_message(filters.command("permissions") & filters.group)
async def check_permissions(client, message):
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.from_user.id

    try:
        member = await client.get_chat_member(chat_id, user_id)
        perms = member.privileges if member.status in ["administrator", "creator"] else None
        text = f"👤 <b>यूजर:</b> {member.user.mention}\n\n🔹 <b>परमिशन:</b> {perms}" if perms else "❌ यह यूजर एक सामान्य सदस्य है।"
        await message.reply_text(text, parse_mode="html")
    except Exception as e:
        await message.reply_text(f"❌ एरर: {e}")

# ✅ **User Full Information**
@app.on_message(filters.command("info") & filters.group)
async def user_info(client, message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        user = message.from_user

    chat_id = message.chat.id
    chat_member = await client.get_chat_member(chat_id, user.id)

    # चेक करें कि यूजर म्यूटेड है या नहीं
    is_muted = chat_member.privileges and not chat_member.privileges.can_send_messages if chat_member.status == ChatMemberStatus.RESTRICTED else False

    # चेतावनियों की संख्या (डेमो के लिए 0)
    warnings = 0  

    text = (
        "📜 User Full Information 📜\n\n"
        f"🆔 ID: {user.id}\n"
        f"🐱 Name: {user.first_name or 'No Name'}\n"
        f"🌍 Username: @{user.username if user.username else 'No username'}\n"
        f"👀 Situation: {'Admin' if chat_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] else 'Member'}\n"
        f"⚠️ Warnings: {warnings}/3\n"
        f"🔇 Muted: {'Yes' if is_muted else 'No'}\n"
        f"⏳ Join Date: {chat_member.joined_date.strftime('%Y-%m-%d %H:%M:%S') if chat_member.joined_date else 'Unknown'}\n"
    )

    await message.reply_text(text)

# ✅ **Admin Panel (Buttons)**
@app.on_message(filters.command("adminpanel") & filters.group & filters.create(is_admin))
async def admin_panel(client, message):
    user = message.reply_to_message.from_user if message.reply_to_message else None

    if not user:
        await message.reply_text("❌ कृपया पहले किसी यूजर को रिप्लाई करें।")
        return

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚫 Ban", callback_data=f"ban_{user.id}"),
            InlineKeyboardButton("🔇 Mute", callback_data=f"mute_{user.id}")
        ],
        [
            InlineKeyboardButton("⚠️ Warn", callback_data=f"warn_{user.id}"),
            InlineKeyboardButton("👤 Info", callback_data=f"info_{user.id}")
        ],
        [
            InlineKeyboardButton("🔍 Profile", url=f"https://t.me/{user.username}") if user.username else InlineKeyboardButton("❌ कोई यूजरनेम नहीं", callback_data="no_username")
        ]
    ])

    await message.reply_text(f"🔧 <b>मॉडरेशन पैनल</b> - {user.mention}", reply_markup=buttons, parse_mode="html")

# ✅ **बॉट रन करें**
print("🤖 Bot is running...")
app.run()
