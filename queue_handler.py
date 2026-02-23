import asyncio
from telethon.errors import FloodWaitError, PeerIdInvalidError
from db_handler import sent_users, usernames_db, save_to_db, blocked_users
from config import MESSAGE_DELAY, TEXT_TEMPLATE, START_PRICE

async def process_queue(client, QUEUE_CHAT, DB_CHAT, price):
    """Обрабатываем очередь: отправка сообщений пользователям"""
    while True:
        async for msg in client.iter_messages(QUEUE_CHAT, limit=20):
            if not msg.text or not msg.text.startswith("#QUEUE"):
                continue
            try:
                username, orig_chat = msg.text.split("\n")[1].split("|")
                orig_chat = int(orig_chat.strip())
            except:
                continue

            try:
                user = await client.get_entity(username.strip())
                if user.bot or ("bot" in (user.username or "").lower()):
                    await msg.delete()
                    continue

                if user.id in sent_users:
                    await msg.delete()
                    continue

                sent = False
                while not sent:
                    try:
                        await client.send_message(user, TEXT_TEMPLATE.format(price=price))
                        sent = True
                    except FloodWaitError as e:
                        await asyncio.sleep(e.seconds)
                    except PeerIdInvalidError:
                        blocked_users[user.id] = user.username or user.first_name
                        sent = True
                    except Exception:
                        blocked_users[user.id] = user.username or user.first_name
                        sent = True

                await save_to_db(user, client, DB_CHAT)
                await msg.delete()
                await client.send_message(orig_chat, f"✅ Написал {username}")
                await asyncio.sleep(MESSAGE_DELAY)

            except Exception as e:
                await client.send_message(orig_chat, f"❌ Ошибка {username}: {e}")
        await asyncio.sleep(5)
