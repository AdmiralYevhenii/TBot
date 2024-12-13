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
                    "!help - отримати список доступних команд"
                )
                asyncio.run(send_message(chat_id, help_text))
            else:
                asyncio.run(send_message(chat_id, "Невідома команда. Використовуйте '!help' для допомоги."))
    
    return "OK", 200

if __name__ == "__main__":
    # Встановлення вебхука
    bot = Bot(token=TOKEN)
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

    # Запускаємо Flask сервер
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
