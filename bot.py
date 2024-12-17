from flask import Flask, request
from telegram import Bot
import os
import time
import asyncio

# Токен бота
TOKEN = "8029573466:AAFq4B_d-s73bPG0z9kRcOAU2sE3wFwAsj4"
WEBHOOK_URL = "https://tbot-pexl.onrender.com"  # URL на Render
BOT_USERNAME = "PidpuvasBot"  # Ім'я бота

app = Flask(__name__)

# Зберігаємо статистику користувачів
user_char_count = {}
user_last_message_time = {}

# Ініціалізуємо бот
bot = Bot(token=TOKEN)

async def send_message(chat_id, text, message_id=None):
    """Асинхронна функція для відправки повідомлення як відповідь."""
    await bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=message_id)

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        message_id = update["message"]["message_id"]
        username = update["message"]["from"]["first_name"]
        text = update["message"].get("text", "")
        message_time = time.time()

        # Логування отриманого тексту
        print(f"Received message: {text}")

        # Оновлюємо кількість символів для користувача
        if username not in user_char_count:
            user_char_count[username] = 0
            user_last_message_time[username] = message_time

        if message_time - user_last_message_time[username] > 600:
            user_char_count[username] = 0

        user_char_count[username] += len(text)
        user_last_message_time[username] = message_time

        # Ігнорування команд, адресованих іншому боту
        if "@" in text:
            if BOT_USERNAME not in text:
                return "OK", 200  # Ігноруємо команду, якщо вона для іншого бота

        # Перевірка на команду
        if text.startswith("/"):
            if text.lower().startswith("/whoiam"):
                from commands import handle_whoiam  # Імпорт всередині функції
                await handle_whoiam(chat_id, bot)
            elif text.lower().startswith("/help"):
                from commands import handle_help  # Імпорт всередині функції
                await handle_help(chat_id, bot)
            elif text.lower().startswith("/shishka"):
                from commands import handle_shishka  # Імпорт всередині функції
                await handle_shishka(chat_id, bot)
            elif text.lower().startswith("/cocktail"):
                from commands import handle_cocktail  # Імпорт всередині функції
                await handle_cocktail(chat_id, bot)
            else:
                await send_message(chat_id, "Невідома команда. Використовуйте '/help' для допомоги.", message_id)

    return "OK", 200

if __name__ == "__main__":
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
