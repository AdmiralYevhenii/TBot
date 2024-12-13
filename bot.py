from flask import Flask, request
from telegram import Bot
import os
import random
import asyncio

# Токен бота
TOKEN = "8029573466:AAFq4B_d-s73bPG0z9kRcOAU2sE3wFwAsj4"
WEBHOOK_URL = "https://tbot-pexl.onrender.com"  # URL на Render

app = Flask(__name__)

# Читання списку відповідей з файлу
def load_responses():
    with open("responses.txt", "r", encoding="utf-8") as file:
        return file.readlines()

responses = load_responses()

# Словник для зберігання кількості символів, надрукованих кожним користувачем
user_char_count = {}

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
        text = update["message"].get("text", "")
        user_name = update["message"]["from"].get("first_name", "Невідомий")

        # Рахуємо кількість символів
        char_count = len(text)
        if user_name in user_char_count:
            user_char_count[user_name] += char_count
        else:
            user_char_count[user_name] = char_count
        
        # Перевірка, чи команда починається з "!".
        if text.startswith("!"):
            # Якщо команда "!хто я?"
            if text.lower() == "!хто я?":
                random_response = random.choice(responses).strip()
                asyncio.run(send_message(chat_id, random_response))
            # Якщо команда "!help"
            elif text.lower() == "!help":
                help_text = (
                    "Команди бота:\n"
                    "!хто я? - отримати випадкову відповідь про себе\n"
                    "!шишка - отримати випадкову шишку\n"
                    "!напиздів - отримати кількість символів, написаних вами\n"
                    "!help - отримати список доступних команд"
                )
                asyncio.run(send_message(chat_id, help_text))
            # Якщо команда "!шишка"
            elif text.lower() == "!шишка":
                shishka_response = generate_shishka()
                asyncio.run(send_message(chat_id, shishka_response))
            # Якщо команда "!напиздів"
            elif text.lower() == "!напиздів":
                user_characters = user_char_count.get(user_name, 0)
                asyncio.run(send_message(chat_id, f"Ти напиздів {user_characters} символів."))
            else:
                asyncio.run(send_message(chat_id, "Невідома команда. Використовуйте '!help' для допомоги."))
        
        # Якщо повідомлення містить слово "колос"
        if "колос" in text.lower():
            asyncio.run(send_message(chat_id, "колос для мужиків"))

    return "OK", 200

if __name__ == "__main__":
    # Встановлення вебхука
    bot = Bot(token=TOKEN)
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

    # Запускаємо Flask сервер
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
