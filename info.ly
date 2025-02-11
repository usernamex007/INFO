from telethon.sync import TelegramClient
from telethon.errors import UsernameInvalidError, UsernameNotOccupiedError

# Telegram API Details (अपनी API ID और API HASH डालें)
API_ID = 28795512  # अपना API ID डालें
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"  # अपना API HASH डालें

# चैनल या ग्रुप का username दें (@ के बिना)
username = "SWEEETY20_200"  

async def get_channel_info():
    async with TelegramClient("session_name", API_ID, API_HASH) as client:
        try:
            entity = await client.get_entity(username)
            
            # जानकारी निकालें
            creator = None
            if entity.creator:
                creator = entity.username if entity.username else "Unknown"

            creation_date = entity.date if entity.date else "Unknown"

            print(f"🔹 Channel/Group Name: {entity.title}")
            print(f"🔹 Creator Username: {creator}")
            print(f"🔹 Creation Date: {creation_date}")
            print(f"🔹 ID: {entity.id}")
            print(f"🔹 Participants Count: {entity.participants_count if hasattr(entity, 'participants_count') else 'Unknown'}")

        except UsernameInvalidError:
            print("❌ Invalid Username!")
        except UsernameNotOccupiedError:
            print("❌ Username not found!")
        except Exception as e:
            print(f"❌ Error: {e}")

# Run the function
import asyncio
asyncio.run(get_channel_info())
