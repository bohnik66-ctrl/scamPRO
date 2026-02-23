from telethon import events, Button
from db_handler import answered_users, blocked_users, usernames_db
from queue_handler import process_queue
from  config import PAGE_SIZE, START_PRICE, DB_CHAT, QUEUE_CHAT, MESSAGE_DELAY, TEXT_TEMPLATE
import asyncio

pages_state = {}
current_price = START_PRICE

def register_commands(client):

    @client.on(events.NewMessage(outgoing=True))
    async def cmd_price(event):
        global current_price
        if not event.text.startswith(".price"):
            return
        try:
            current_price = int(event.text.split(" ")[1])
            await event.respond(f"💰 Новая цена: {current_price}")
        except:
            await event.respond("❌ Формат: .price 950")

    @client.on(events.NewMessage(outgoing=True))
    async def cmd_send(event):
        if not event.text.startswith(".send"):
            return
        if not event.is_reply:
            await event.respond("❗ Ответь на сообщение с юзерами")
            return
        msg = await event.get_reply_message()
        import re
        users = re.findall(r"@[\w\d_]{4,}", msg.text)
        if not users:
            await event.respond("❌ Юзернеймы не найдены")
            return
        for username in users:
            await client.send_message(QUEUE_CHAT, f"#QUEUE\n{username} | {event.chat_id}")
        await event.respond(f"👀 Добавлено {len(users)} в очередь")
        asyncio.create_task(process_queue(client, QUEUE_CHAT, DB_CHAT, current_price))

    @client.on(events.NewMessage(outgoing=True))
    async def cmd_answers(event):
        if not event.text.startswith(".answers"):
            return
        answered_list = list(set(answered_users.values()))
        if not answered_list:
            await event.respond("❌ Ответов пока нет")
            return
        await send_paged_message(client, event.chat_id, answered_list, "Ответившие")

    @client.on(events.NewMessage(outgoing=True))
    async def cmd_blocked(event):
        if not event.text.startswith(".blocked"):
            return
        blocked_list = blocked_users.values()
        if not blocked_list:
            await event.respond("✅ Никто не заблокировал")
            return
        await event.respond(f"⛔ Заблокировали ({len(blocked_list)}):\n" + "\n".join(blocked_list))

    async def send_paged_message(client, chat_id, items_list, title):
        total_pages = (len(items_list) - 1) // PAGE_SIZE + 1
        page = 1
        start = 0
        end = PAGE_SIZE
        text = f"{title} (страница {page}/{total_pages}):\n" + "\n".join(items_list[start:end])
        buttons = []
        if total_pages > 1:
            buttons.append(Button.inline("➡️ Вперед", f"next_{chat_id}"))
        msg = await client.send_message(chat_id, text, buttons=buttons)
        pages_state[msg.id] = (items_list, page, title)

    @client.on(events.CallbackQuery)
    async def callback(event):
        data = event.data.decode("utf-8")
        msg_id = event.message.id
        if msg_id not in pages_state:
            await event.answer("❌ Страницы не найдены")
            return
        list_items, current_page, title = pages_state[msg_id]
        if data.startswith("next_"):
            page = current_page + 1
        elif data.startswith("prev_"):
            page = current_page - 1
        else:
            await event.answer()
            return
        total_pages = (len(list_items) - 1) // PAGE_SIZE + 1
        if page < 1 or page > total_pages:
            await event.answer("❌ Нет такой страницы")
            return
        start = (page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        text = f"{title} (страница {page}/{total_pages}):\n" + "\n".join(list_items[start:end])
        buttons = []
        if page > 1:
            buttons.append(Button.inline("⬅️ Назад", f"prev_{msg_id}"))
        if page < total_pages:
            buttons.append(Button.inline("➡️ Вперед", f"next_{msg_id}"))
        pages_state[msg_id] = (list_items, page, title)
        await event.edit(text, buttons=buttons)
