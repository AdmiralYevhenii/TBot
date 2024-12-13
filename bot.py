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

# Словник для зберігання кількості символів і часу для кожного користувача
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
    
    return f"Твоя шишка {random_choice} см" if random_choice != 1 else f"Твоя шишка {random_choice} см, їбать ти лох"  # Для випадку, якщо випало 1

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        user_name = update["message"]["from"].get("first_name", "Невідомий")
        current_time = time.time()  # поточний час в секундах
        
        # Перевірка на наявність користувача в словнику
        if chat_id not in user_char_count:
            user_char_count[chat_id] = 0
            user_last_message_time[chat_id] = current_time
        
        # Рахуємо кількість символів в повідомленні
        message_length = len(text)

        # Перевірка, чи перевищує кількість символів 800 за останні 10 хвилин
        time_difference = current_time - user_last_message_time[chat_id]
        if time_difference <= 600:  # 10 хвилин = 600 секунд
            user_char_count[chat_id] += message_length
        else:
            user_char_count[chat_id] = message_length  # Скидаємо лічильник, якщо час між повідомленнями більше 10 хвилин

        # Оновлюємо час останнього повідомлення
        user_last_message_time[chat_id] = current_time

        if user_char_count[chat_id] >= 800:
            # Якщо кількість символів перевищує 800 за останні 10 хвилин
            if user_name == "Денис":  # Перевірка на ім'я
                asyncio.run(send_message(chat_id, "Денис, сходи попісяй"))
                # Скидаємо лічильник після відправлення повідомлення
                user_char_count[chat_id] = 0
        
        # Перевірка, чи команда починається з "!"
        if text.startswith("!"):
            if text.lower() == "!хто я?":
                random_response = random.choice(responses).strip()
                asyncio.run(send_message(chat_id, random_response))
            elif text.lower() == "!help":
                help_text = (
                    "Команди бота:\n"
                    "!хто я? - Дізнайся хто ти\n"
                    "!шишка - Показати всім якого розміру твоя шишка""
                )
                asyncio.run(send_message(chat_id, help_text))
            elif text.lower() == "!шишка":
                shishka_response = generate_shishka()
                asyncio.run(send_message(chat_id, shishka_response))
            else:
                asyncio.run(send_message(chat_id, "Невідома команда. Використовуйте '!help' для допомоги."))
        # Реакція на конкретне слово "колос"
        elif "колос" in text.lower():
            asyncio.run(send_message(chat_id, "колос для мужиків"))
    
    return "OK", 200

if __name__ == "__main__":
    bot = Bot(token=TOKEN)
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
