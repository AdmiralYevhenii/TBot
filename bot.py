from flask import Flask, request
from telegram import Bot
import os
import random
import time
import json
import openai
import logging
from collections import defaultdict

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Токен бота
TOKEN = os.environ.get("8029573466:AAFq4B_d-s73bPG0z9kRcOAU2sE3wFwAsj4")
WEBHOOK_URL = os.environ.get("https://tbot-pexl.onrender.com")  # URL на Render
BOT_USERNAME = os.environ.get("PidpuvasBot")  # Ім'я бота
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Зберігаємо статистику користувачів
user_char_count = defaultdict(int)
user_last_message_time = defaultdict(lambda: 0)

# Читання списку відповідей з файлу
def load_responses():
    with open("responses.txt", "r", encoding="utf-8") as file:
        return file.readlines()

responses = load_responses()

# Функція для обробки запитів до OpenAI
def ask_openai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Виникла помилка під час звернення до OpenAI: {str(e)}"

# Функція для відправки повідомлення
def send_message_sync(chat_id, text, message_id=None):
    bot = Bot(token=TOKEN)
    bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=message_id)

# Маршрут для вебхука
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    logging.info(f"Received update: {json.dumps(update, ensure_ascii=False)}")

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        message_id = update["message"]["message_id"]
        username = update["message"]["from"]["first_name"]
        text = update["message"].get("text", "")
        message_time = time.time()

        # Логування отриманого тексту
        logging.info(f"Received message: {text}")

        # Оновлюємо кількість символів для користувача
        if username not in user_char_count:
            user_char_count[username] = 0
            user_last_message_time[username] = message_time

        if message_time - user_last_message_time[username] > 600:
            user_char_count[username] = 0

        user_char_count[username] += len(text)
        user_last_message_time[username] = message_time

        # Перевірка на 800 символів
        if user_char_count[username] >= 800:
            send_message_sync(chat_id, f"{username}, сходи попісяй", message_id)
            user_char_count[username] = 0

        # Ігнорування команд, адресованих іншому боту
        if "@" in text and BOT_USERNAME not in text:
            return "OK", 200

        # Перевірка на команду
        if text.startswith("/"):
            if text.lower().startswith("/whoiam"):
                random_response = random.choice(responses).strip()
                send_message_sync(chat_id, f"{random_response}", message_id)
            elif text.lower().startswith("/help"):
                help_text = (
                    "Команди бота:\n"
                    "/whoiam - Дізнайся хто ти\n"
                    "/shishka - Показати всім розмір твоєї шишки\n"
                    "/cocktail - Отримати випадковий коктейль\n"
                    "/ask - Задати запитання OpenAI"
                )
                send_message_sync(chat_id, help_text, message_id)
            elif text.lower().startswith("/shishka"):
                shishka_response = generate_shishka()
                send_message_sync(chat_id, f"{shishka_response}", message_id)
            elif text.lower().startswith("/cocktail"):
                cocktails = load_cocktails()
                cocktail = random.choice(cocktails)
                ingredients = "\n".join(cocktail["ingredients"])
                preparation = cocktail["preparation"]
                cocktail_response = (
                    f"Коктейль: {cocktail['name']}\n"
                    f"Складові:\n{ingredients}\n"
                    f"Як приготувати:\n{preparation}"
                )
                send_message_sync(chat_id, cocktail_response, message_id)
            elif text.lower().startswith("/ask"):
                prompt = text[5:].strip()  # Забираємо команду і залишаємо лише текст запиту
                if prompt:
                    openai_response = ask_openai(prompt)
                    send_message_sync(chat_id, openai_response, message_id)
                else:
                    send_message_sync(chat_id, "Будь ласка, введіть текст запиту після команди /ask.", message_id)

    return "OK", 200

if __name__ == "__main__":
    bot = Bot(token=TOKEN)
    bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")  # Використовуємо новий маршрут
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))