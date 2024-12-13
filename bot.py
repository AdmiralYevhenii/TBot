from flask import Flask, request
from telegram import Bot
from telegram.utils.request import Request
import os
import asyncio

# Токен бота 
TOKEN = "8029573466:AAFq4B_d-s73bPG0z9kRcOAU2sE3wFwAsj4"  # токен бота
WEBHOOK_URL = "https://tbot-pexl.onrender.com"  # URL на Render

# Налаштування пулу з'єднань
request = Request(con_pool_size=8)  # Збільшуємо розмір пулу
bot = Bot(token=TOKEN, request=request)
app = Flask(__name__)

async def send_message(chat_id, text):
    """Асинхронна функція для відправки повідомлення."""
    await bot.send_message(chat_id=chat_id, text=text)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        
        # Використовуємо асинхронне відправлення повідомлення
        if text.lower() == "хто я?":
            asyncio.run(send_message(chat_id, "Хто ми?"))
        else:
            asyncio.run(send_message(chat_id, f"Ви сказали: {text}"))
    
    return "OK", 200

if __name__ == "__main__":
    # Встановлення вебхука
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
