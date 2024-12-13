from flask import Flask, request
from telegram import Bot
import os
import random
import asyncio
import time

# Токен бота
TOKEN = "8029573466:AAFq4B_d-s73bPG0z9kRcOAU2sE3wFwAsj4"
WEBHOOK_URL = "https://tbot-pexl.onrender.com"  # URL на Render

app = Flask(__name__)

# Зберігаємо статистику користувачів: кількість символів та час останнього повідомлення
user_char_count = {}
user_last_message_time = {}

# Читання списку відповідей з файлу
def load_responses():
    with open("responses.txt", "r", encoding="utf-8") as file:
        return file.readlines()

responses = load_responses()

async def send_message(chat_id, text):
    """Асинхронна функція для відправки повідомлення."""
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=chat_id, text=text)

# Функція для генерації шишки
def generate_shishka():
    random_choice = random.choices(
        [random.randint(5, 15), random.randint(15, 20), random.randint(20, 25), random.randint(25, 30), 1], 
        weights=[50, 25, 10, 5, 1], k=1
    )[0]
    
    # Визначаємо, в який діапазон потрапило число
    if 5 <= random_choice <= 15:
        return f"Твоя шишка {random_choice} см"
    elif 15 < random_choice <= 20:
        return f"Твоя шишка {random_choice} см"
    elif 20 < random_choice <= 25:
        return f"Твоя шишка {random_choice} см"
    elif 25 < random_choice <= 30:
        return f"Твоя шишка {random_choice} см"
    else:
        return f"Твоя шишка {random_choice} см, їбать ти лох"  # Для випадку, якщо випало 1

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        username = update["message"]["from"]["first_name"]
        text = update["message"].get("text", "")
        message_time = time.time()  # Час відправлення повідомлення

        # Оновлюємо кількість символів для користувача
        if username not in user_char_count:
            user_char_count[username] = 0
            user_last_message_time[username] = message_time

        # Якщо між поточним і останнім повідомленням більше ніж 10 хвилин, скидаємо лічильник
        if message_time - user_last_message_time[username] > 600:
            user_char_count[username] = 0

        # Додаємо кількість символів цього повідомлення до лічильника
        user_char_count[username] += len(text)

        # Оновлюємо час останнього повідомлення
        user_last_message_time[username] = message_time

        # Перевірка, чи користувач перевищив 800 символів за останні 10 хвилин
        if user_char_count[username] >= 800:
            asyncio.run(send_message(chat_id, f"@{username}, сходи попісяй"))
            user_char_count[username] = 0  # Скидаємо лічильник після відповіді

        # Перевірка, чи команда починається з "!"
        if text.startswith("!"):
            # Якщо команда "!хто я?"
            if text.lower() == "!хто я?":
                random_response = random.choice(responses).strip()
                asyncio.run(send_message(chat_id, random_response))
            # Якщо команда "!help"
            elif text.lower() == "!help":
                help_text = (
                    "Команди бота:\n"
                    "!хто я? - Дізнайся хто ти\n"
                    "!шишка - Показати всім якого розміру твоя шишка"
                )
                asyncio.run(send_message(chat_id, help_text))
            # Якщо команда "!шишка"
            elif text.lower() == "!шишка":
                shishka_response = generate_shishka()
                asyncio.run(send_message(chat_id, shishka_response))
            else:
                asyncio.run(send_message(chat_id, "Невідома команда. Використовуйте '!help' для допомоги."))
        # Якщо в чаті зустрічається слово "колос"
        elif "колос" in text.lower():
            asyncio.run(send_message(chat_id, "колос для підарів"))
    
    return "OK", 200

if __name__ == "__main__":
    # Встановлення вебхука
    bot = Bot(token=TOKEN)
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

    # Запускаємо Flask сервер
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
