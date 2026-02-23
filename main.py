from telethon import TelegramClient
from config import API_ID, API_HASH
from commands_handler import register_commands
from events_handler import register_events

client = TelegramClient("session", API_ID, API_HASH)

register_commands(client)
register_events(client)

async def main():
    await client.start()
    print("✅ Юзербот запущен")
    await client.run_until_disconnected()

import asyncio
asyncio.run(main())
