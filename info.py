import asyncio
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.errors import UsernameInvalidError, UsernameNotOccupiedError

# Telegram API Details (अपनी API ID और API HASH डालें)
API_ID = 28795512  # अपना API ID डालें
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"  # अपना API HASH डालें
BOT_TOKEN = "7589052839:AAGPMVeZpb63GEG_xXzQEua1q9ewfNzTg50"  # अपना बॉट टोकन डालें

# Support Links
SUPPORT_CHANNEL = "https://t.me/SANATANI_TECJ"
SUPPORT_GROUP = "https://t.me/SANATANI_SUPPORT"

# Telethon Client Setup
bot = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# /start Command
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    buttons = [
        [Button.inline("🔍 Get Info", data="get_info")],
        [Button.url("📢 Support Channel", SUPPORT_CHANNEL), Button.url("💬 Support Group", SUPPORT_GROUP)]
    ]

    await event.respond(
        "**👋 Welcome to Telegram Info Bot!**\n\n"
        "➤ इस बॉट से आप किसी भी **Telegram Group या Channel** की पूरी जानकारी निकाल सकते हैं।\n"
        "➤ बस **Get Info** बटन दबाएं और Username दें।\n\n"
        "🔥 **Features:**\n"
        "✅ Group/Channel Name\n"
        "✅ Owner (Creator) Name & Username\n"
        "✅ Creation Date\n"
        "✅ Participants Count\n"
        "✅ Latest 10 Joined Users\n\n"
        "👇 नीचे बटन से शुरू करें!",
        buttons=buttons
    )

# Callback for "Get Info" Button
@bot.on(events.CallbackQuery(data="get_info"))
async def ask_for_username(event):
    await event.respond("📌 **Please enter the username of the Channel/Group (without @):**")

# Info Command
@bot.on(events.NewMessage(pattern="^[^/].+"))  # कोई भी Normal Text पर Trigger होगा
async def get_channel_info(event):
    username = event.raw_text.strip()
    try:
        entity = await bot.get_entity(username)
        full_info = await bot(GetFullChannelRequest(entity))
        creator = "Unknown"
        creator_username = "Unknown"
        creator_id = "Unknown"

        # Creator की Details निकालें
        if full_info.full_chat.creator_id:
            creator_id = full_info.full_chat.creator_id
            creator_user = await bot.get_entity(creator_id)
            creator = creator_user.first_name + (" " + creator_user.last_name if creator_user.last_name else "")
            creator_username = "@" + creator_user.username if creator_user.username else "No Username"

        # Participants Count
        participants_count = full_info.full_chat.participants_count if hasattr(full_info.full_chat, 'participants_count') else 'Unknown'

        # Joined Users की List निकालें (Latest 10 Members)
        users = await bot.get_participants(entity)
        latest_users = users[:10] if len(users) > 10 else users
        user_list = "\n".join([f"🔹 {u.first_name} ({'@' + u.username if u.username else 'No Username'})" for u in latest_users])

        info_text = (
            f"🔹 **Channel/Group Name:** `{entity.title}`\n"
            f"🔹 **Creator Name:** `{creator}`\n"
            f"🔹 **Creator Username:** {creator_username}\n"
            f"🔹 **Creator ID:** `{creator_id}`\n"
            f"🔹 **Creation Date:** `{entity.date}`\n"
            f"🔹 **ID:** `{entity.id}`\n"
            f"🔹 **Participants Count:** `{participants_count}`\n\n"
            f"👥 **Recent 10 Users:**\n{user_list if user_list else 'No Users Found'}"
        )

        await event.respond(info_text)

    except UsernameInvalidError:
        await event.respond("❌ Invalid Username!")
    except UsernameNotOccupiedError:
        await event.respond("❌ Username not found!")
    except Exception as e:
        await event.respond(f"❌ Error: {e}")

print("✅ Bot is Running...")
bot.run_until_disconnected()
