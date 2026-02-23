sent_users = set()          # кому уже писали
answered_users = {}         # id -> username
blocked_users = {}          # id -> username
usernames_db = {}           # id -> username

from logger import log_error

async def save_to_db(user, client, DB_CHAT):
    """Сохраняем пользователя в DB_CHAT"""
    try:
        await client.send_message(DB_CHAT, f"#DB\n{user.id} | @{user.username or 'no_username'}")
    except Exception as e:
        log_error(f"Ошибка сохранения в DB_CHAT {user.username}: {e}")
    sent_users.add(user.id)
    usernames_db[user.id] = user.username or user.first_name
