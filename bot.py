from flask import Flask, request
from telegram import Bot
import os
import asyncio
from datetime import datetime, timedelta

# Токен вашого бота
TOKEN = "8029573466:AAFq4B_d-s73bPG0z9kRcOAU2sE3wFwAsj4"
WEBHOOK_URL = "https://tbot-pexl.onrender.com"  # Ваш URL на Render

app = Flask(__name__)

# Словник для зберігання даних про кількість символів
user_activity = {}

# Часовий ліміт для перевірки
TIME_LIMIT = timedelta(minutes=10)
SYMBOL_LIMIT = 800

# Ім'я користувача Дениса
TARGET_USERNAME = "Просто існую"  # Замініть на справжнє ім'я користувача

async def send_message(chat_id, text):
    """Асинхронна функція для відправки повідомлення."""
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=chat_id, text=text)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        user = update["message"]["from"]  # Дані про автора повідомлення
        username = user.get("username", "Unknown")

        # Якщо повідомлення від цільового користувача
        if username == TARGET_USERNAME:
            current_time = datetime.utcnow()

            # Оновлюємо дані про активність
            if username not in user_activity:
                user_activity[username] = []

            # Додаємо нове повідомлення до записів
            user_activity[username].append({"time": current_time, "length": len(text)})

            # Видаляємо старі записи (старше ніж 10 хвилин)
            user_activity[username] = [
                entry for entry in user_activity[username]
                if entry["time"] > current_time - TIME_LIMIT
            ]

            # Рахуємо кількість символів за останні 10 хвилин
            total_symbols = sum(entry["length"] for entry in user_activity[username])

            # Якщо кількість символів перевищила ліміт
            if total_symbols > SYMBOL_LIMIT:
                asyncio.run(send_message(chat_id, "Денис, сходи попісяй"))
                # Очищаємо лічильник після попередження
                user_activity[username] = []

    return "OK", 200

if __name__ == "__main__":
    # Встановлення вебхука
    bot = Bot(token=TOKEN)
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

    # Запускаємо Flask сервер
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
