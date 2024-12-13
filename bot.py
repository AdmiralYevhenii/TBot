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
    try:
        with open("responses.txt", "r", encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError:
        return ["Файл спиздили, або він оновлюється."]
        
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
    
    if random_choice == 1:
        return "Твоя шишка 1 см, їбать ти лох"
    return f"Твоя шишка {random_choice} см"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        
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
                    "!help - отримати список доступних команд"
                )
                asyncio.run(send_message(chat_id, help_text))
            # Якщо команда "!шишка"
            elif text.lower() == "!шишка":
                shishka_response = generate_shishka()
                asyncio.run(send_message(chat_id, shishka_response))
            else:
                asyncio.run(send_message(chat_id, "Невідома команда. Використовуйте '!help' для допомоги."))
        # Реакція на слово "колос"
        elif "колос" in text.lower():
            asyncio.run(send_message(chat_id, "колос для ~підорів~ мужиків"))
    
    return "OK", 200

if __name__ == "__main__":
    # Встановлення вебхука
    bot = Bot(token=TOKEN)
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

    # Запускаємо Flask сервер
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
