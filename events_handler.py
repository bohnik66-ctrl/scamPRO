from telethon import events
from db_handler import answered_users, usernames_db, save_to_db
from config import DB_CHAT
def register_events(client):
    @client.on(events.NewMessage(incoming=True))
    async def catch_answers(event):
        if not event.is_private:
            return
        user = await event.get_sender()
        if user.bot or ("bot" in (user.username or "").lower()):
            return
        if user.id not in answered_users:
            answered_users[user.id] = user.username or user.first_name
            await save_to_db(user, client, DB_CHAT)
