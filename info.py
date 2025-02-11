import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.errors import UsernameInvalidError, UsernameNotOccupiedError

# Telegram API Details (अपनी API ID और API HASH डालें)
API_ID = 28795512  # अपना API ID डालें
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"  # अपना API HASH डालें
BOT_TOKEN = "7589052839:AAGPMVeZpb63GEG_xXzQEua1q9ewfNzTg50"  # अपना बॉट टोकन डालें

# Telethon Client Setup
bot = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern="/info (.+)"))
async def get_channel_info(event):
    username = event.pattern_match.group(1).strip()
    try:
        entity = await bot.get_entity(username)
        full_info = await bot(GetFullChannelRequest(entity))
        creator = "Unknown"
        creator_username = "Unknown"

        # Creator की Details निकालें
        for user in full_info.users:
            if user.id == entity.creator_id:
                creator = user.first_name + (" " + user.last_name if user.last_name else "")
                creator_username = "@" + user.username if user.username else "No Username"
                break

        info_text = (
            f"🔹 **Channel/Group Name:** `{entity.title}`\n"
            f"🔹 **Creator Name:** `{creator}`\n"
            f"🔹 **Creator Username:** {creator_username}\n"
            f"🔹 **Creation Date:** `{entity.date}`\n"
            f"🔹 **ID:** `{entity.id}`\n"
            f"🔹 **Participants Count:** `{entity.participants_count if hasattr(entity, 'participants_count') else 'Unknown'}`"
        )

        await event.reply(info_text)

    except UsernameInvalidError:
        await event.reply("❌ Invalid Username!")
    except UsernameNotOccupiedError:
        await event.reply("❌ Username not found!")
    except Exception as e:
        await event.reply(f"❌ Error: {e}")

print("✅ Bot is Running...")
bot.run_until_disconnected()
