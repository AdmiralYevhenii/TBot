from flask import Flask, request
from telegram import Bot
import os

# Токен бота
TOKEN = "8029573466:AAFq4B_d-s73bPG0z9kRcOAU2sE3wFwAsj4"  # Замініть на ваш реальний токен
WEBHOOK_URL = "https://tbot-pexl.onrender.com"  # Замініть на ваш URL на Render

bot = Bot(token=TOKEN)
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    # Обробка повідомлення
    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"]
    bot.send_message(chat_id=chat_id, text=f"Ви сказали: {text}")
    return "OK", 200

if __name__ == "__main__":
    # Встановлення вебхука
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
