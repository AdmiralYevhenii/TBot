from flask import Flask, request
from telegram import Bot
import os
import random
import time
import json
import logging
from collections import defaultdict
import openai

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Отримання OpenAI API ключа
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Не знайдено OpenAI API ключ у змінних оточення.")

openai.api_key = OPENAI_API_KEY

# Токен бота
TOKEN = "8029573466:AAFq4B_d-s73bPG0z9kRcOAU2sE3wFwAsj4"
WEBHOOK_URL = "https://tbot-pexl.onrender.com"
BOT_USERNAME = "PidpuvasBot"

app = Flask(__name__)

# Зберігаємо статистику користувачів
user_char_count = defaultdict(int)
user_last_message_time = defaultdict(lambda: 0)

# Читання списку відповідей з файлу
def load_responses():
    with open("responses.txt", "r", encoding="utf-8") as file:
        return file.readlines()

responses = load_responses()

# Читання списку коктейлів з файлу
def load_cocktails():
    with open("cocktails.json", "r", encoding="utf-8") as file:
        return json.load(file)

def send_message_sync(chat_id, text, message_id=None):
    """Синхронна функція для відправки повідомлення як відповідь."""
    bot = Bot(token=TOKEN)
    bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=message_id)

def generate_shishka():
    random_choice = random.choices(
        [random.randint(5, 15), random.randint(15, 20), random.randint(20, 25), random.randint(25, 30), 1], 
        weights=[50, 25, 10, 5, 1], k=1
    )[0]
    return f"Твоя шишка {random_choice} см" if random_choice != 1 else "Твоя шишка 1 см, їбать ти лох"

def get_openai_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ти є корисним помічником."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Помилка: {str(e)}"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    logging.info(f"Received update: {json.dumps(update, ensure_ascii=False)}")

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        message_id = update["message"]["message_id"]
        username = update["message"]["from"]["first_name"]
        text = update["message"].get("text", "")
        message_time = time.time()

        if text.startswith("/ask"):
            prompt = text[len("/ask "):].strip()
            response = get_openai_response(prompt) if prompt else "Будь ласка, напишіть запит після команди /ask."
            send_message_sync(chat_id, response, message_id)

        user_char_count[username] += len(text)
        user_last_message_time[username] = message_time

        if user_char_count[username] >= 800:
            send_message_sync(chat_id, f"{username}, сходи попісяй", message_id)
            user_char_count[username] = 0

        if text.startswith("/whoiam"):
            random_response = random.choice(responses).strip()
            send_message_sync(chat_id, random_response, message_id)

    return "OK", 200

if __name__ == "__main__":
    bot = Bot(token=TOKEN)
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
